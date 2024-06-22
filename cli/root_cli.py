import datetime

import humanize
from cli.project_view_cli import ProjectViewCLI
from models.task_model import Status, Task
from peewee import DoesNotExist
from utils.deltaParser import convertDate
from utils.log import LogCollection
from utils.simple_cli import *
from cli.project_cli import ProjectCLI
from cli.deadline_cli import DeadlineCLI
from services import project_service, task_service, deadline_service
from utils.config import INACTIVE_DAYS
from models.deadline_model import DeadlineStates


class BaseCLI(CLI):
    def __init__(self) -> None:
        super().__init__()
        self.commands = self.generateCommandDict(
            [
                Command("projects", self.openProjectsCommand),
                Command("deadlines", self.openDeadlinesCommand),
                Command("open", self.openProjectCommand, 1),
                Command("active", self.activeCommand),
                # Command("view", self.viewCommand),
                Command("switch", self.switchCommand),
                Command("done", self.doneCommand),
                # Command("due", self.listDeadlinesCommand),
                Command("check-inactive", self.checkInactiveCommand),
                Command("streak", self.streakCommand),
                Command("last-task", self.lastTaskCommand),
                Command("activate", self.activateCommand, 1),
                Command("deactivate", self.deactivateCommand, 1),
            ]
        )
        self.showScreen()

    def showScreen(self):

        Logger.clear()

        Logger.header()

        # show starting text
        # print()
        # self.lastTaskCommand()
        # print()
        # self.streakCommand()
        # print()

        # Logger.heading("CHECKING STATUS")
        # print()
        # # make a project inactive if last task was done before a month
        # self.checkInactiveCommand()
        # print()
        # self.viewCommand()
        # Logger.heading("ACTIVE PROJECTS")
        self.activeCommand()

        print()
        print()

        # Logger.heading("Deadlines")
        # self.listDeadlinesCommand()
        # print()

    def openProjectsCommand(self, args=[]):
        projectCLI = ProjectCLI()

        close = projectCLI.run()
        if close:
            self.close()
        else:
            self.showScreen()

        return close

    def openDeadlinesCommand(self, args=[]):
        deadlineCLI = DeadlineCLI()

        close = deadlineCLI.run()
        if close:
            self.close()
        else:
            self.showScreen()
        return close

    def listDeadlinesCommand(self, args=[]):
        pendingDeadlines = deadline_service.findAllDeadlineState(
            DeadlineStates.PENDING.value
        )

        print()
        count = 0
        for deadline in pendingDeadlines:
            Logger.deadline(deadline)

            if count >= 4:
                break
            count += 1
        print()

    def activeCommand(self, args=[]):
        activeProjects = project_service.getActiveProjects()

        # get current task
        current = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)

        if len(activeProjects) == 0:
            Logger.warn("No Active Projects set!", " ")
            return

        if len(current) == 0:
            currentProject = None

        elif len(current) > 1:
            Logger.warn("There is more than one IN-PROGRESS task set!")
            Logger.warn("Something in the code has gone wrong!")
        else:
            currentProject = current[0].project.id

        for index, project in enumerate(activeProjects):
            complete = task_service.getCompletionForProject(project.id)
            if currentProject != None and currentProject == project.id:
                if index != 0:
                    print()

                print("-" * 68)
                Logger.project(
                    project,
                    complete,
                    highlight=True,
                )
                print("-" * 68)
                Logger.task(current[0], noHighlight=True, noIndex=True)
                print()
            else:
                Logger.project(project, complete)

    def viewCommand(self, args=[]):
        current = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)

        if len(current) == 0:
            Logger.warn("There is no IN-PROGRESS task set")
            print()
            return
        elif len(current) > 1:
            Logger.warn("There is more than one IN-PROGRESS task set!")
            Logger.warn("Something in the code has gone wrong!")

        complete = task_service.getCompletionForProject(current[0].project.id)
        Logger.project(current[0].project, complete)
        print("-" * 68)
        Logger.task(current[0], noHighlight=True, noIndex=True)
        print("" * 68)
        print()

    def switchCommand(self, args=[]):
        """
        switch

        Options:
            default                     change project
            -p | project                change project
            -t | task                   change task within current project
            -rp | random-project        change to random project
            -rt | random-task           change to random task within current project
            -r | random                 change to random task within random project
        """

        isCurrentProject = False
        isProjectRandom = False
        isTaskRandom = False
        projectNumber = None

        logs = LogCollection()

        if len(args) != 0:
            if args[0] in ("project", "-p"):
                projectNumber = args[1] if len(args) > 1 else None
            elif args[0] in ("task", "-t"):
                isCurrentProject = True
            elif args[0] in ("random-project", "-rp"):
                isProjectRandom = True
            elif args[0] in ("random-task", "-rt"):
                isCurrentProject = True
                isTaskRandom = True
            elif args[0] in ("random", "-r"):
                isTaskRandom = True
                isProjectRandom = True
            elif args[0].isnumeric():
                projectNumber = int(args[0])
            else:
                self.showScreen()
                logs.execute()
                Logger.error("Unknown {}: please check documentation".format(args[0]))
                return

        activeProjects = project_service.getActiveProjects(random=isProjectRandom)

        if len(activeProjects) == 0:
            self.showScreen()
            logs.execute()
            Logger.warn("No active projects set!")
            print()
            return

        currentTask = None

        currentTasksQuery = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)

        # Get next project
        if projectNumber != None:
            try:
                nextProject = project_service.getOneProject(projectNumber)
                if not nextProject.active:
                    self.showScreen()
                    logs.execute()
                    Logger.error("Project is not active")
                    return
                if len(currentTasksQuery) != 0:
                    currentTask = currentTasksQuery[0]
                    logs.info(
                        "Setting Task '{}' to BACKLOG...".format(currentTask.name)
                    )
                    currentTask = task_service.updateStatus(
                        currentTask, Status.BACKLOG.value
                    )

            except DoesNotExist:
                self.showScreen()
                logs.execute()
                Logger.error("No project with that id exists!")
                return
        else:
            if len(currentTasksQuery) == 0:
                nextProject = activeProjects[0]
            else:
                currentTask = currentTasksQuery[0]

                # find the next project based on project id
                if not isCurrentProject:
                    nextProjectList = list(
                        filter(
                            lambda x: x.id > currentTask.project.id,
                            list(activeProjects),
                        )
                    )
                    if len(nextProjectList) == 0:
                        nextProject = activeProjects[0]
                    else:
                        nextProject = nextProjectList[0]
                    logs.info("Switching project to '{}'".format(nextProject.name))
                else:
                    nextProject = currentTask.project
                logs.info("Setting Task '{}' to BACKLOG...".format(currentTask.name))
                currentTask = task_service.updateStatus(
                    currentTask, Status.BACKLOG.value
                )

        todoTasksQuery = task_service.findAllTaskStatusForProject(
            Status.BACKLOG.value, nextProject.id, random=isTaskRandom
        )

        if len(todoTasksQuery) == 0:
            self.showScreen()
            logs.execute()
            Logger.error("There is an active project with no BACKLOG tasks")
            raise Exception("Active Project with no BACKLOG task")

        if currentTask == None:
            firstTodo = todoTasksQuery[0]
        else:
            nextTodoList = list(
                filter(lambda x: x.id > currentTask.id, list(todoTasksQuery))
            )
            if len(nextTodoList) == 0:
                firstTodo = todoTasksQuery[0]
            else:
                firstTodo = nextTodoList[0]

        logs.info("Setting Task '{}' to IN-PROGRESS...".format(firstTodo.name))
        task_service.updateStatus(firstTodo, Status.IN_PROGRESS.value)
        logs.success("Tasks have been updated!")

        self.showScreen()
        logs.execute()

    def doneCommand(self, args=[]):
        logs = LogCollection()

        currentTaskQuery = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)
        if len(currentTaskQuery) == 0:
            self.showScreen()
            logs.execute()
            Logger.error("No current task set!")
            return

        currentTask = currentTaskQuery[0]

        todoTasksQuery = task_service.findAllTaskStatusForProject(
            Status.BACKLOG.value, currentTask.project.id
        )

        logs.info(
            "Completion Time: {}".format(
                humanize.naturaldelta(datetime.datetime.now() - currentTask.startDate)
            ),
        )

        logs.info("Setting Task '{}' to DONE...".format(currentTask.name))
        task_service.updateStatus(currentTask, Status.DONE.value)

        if len(todoTasksQuery) == 0:
            logs.success("All tasks in project completed!")
            # logs.celebrate("Project Completed")
            # logs.info("Setting project to inactive...")
            project_service.updateProjectStatus(currentTask.project.id, False)
            logs.success("Project set to inactive!")

            self.showScreen()
            logs.execute()
            return

        firstTodo = todoTasksQuery[0]
        logs.info("Setting Task '{}' to IN-PROGRESS...".format(firstTodo.name))
        task_service.updateStatus(firstTodo, Status.IN_PROGRESS.value)
        logs.success("Tasks have been updated!")

        self.showScreen()
        logs.execute()

    def checkInactiveCommand(self, indent=False, args=[]):
        currentTaskQuery = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)

        currentTask = None
        if len(currentTaskQuery) != 0:
            currentTask = currentTaskQuery[0]

        activeProjects = project_service.getActiveProjects()

        inactiveCount = 0

        indentSpace = ""
        if indent:
            indentSpace = " "

        for project in activeProjects:
            # Check if the project has remained active for long enough
            elapsed = datetime.datetime.now() - project.updated
            if elapsed < datetime.timedelta(days=INACTIVE_DAYS):
                continue

            if currentTask != None:
                if currentTask.project.id == project.id:
                    # Check how long the current task hasn't been completed
                    elapsed = datetime.datetime.now() - currentTask.startDate
                    if elapsed > datetime.timedelta(days=INACTIVE_DAYS):
                        Logger.info(
                            "Project '{}' has not been updated for {} days".format(
                                project.name, INACTIVE_DAYS
                            ),
                            indent=indentSpace,
                        )

                        Logger.info(
                            "Setting Task '{}' to BACKLOG".format(currentTask.name),
                            indent=indentSpace,
                        )
                        task_service.updateStatus(currentTask, Status.BACKLOG.value)

                        Logger.info(
                            "Setting Project '{}' to inactive".format(project.name),
                            indent=indentSpace,
                        )
                        project_service.updateProjectStatus(project.id, False)
                        inactiveCount += 1
                    continue

            DoneTasks = task_service.findAllTaskStatusForProject(
                Status.DONE.value, project.id, orderBy=Task.endDate, desc=True
            )

            if len(DoneTasks) == 0:
                # If project has no completed tasks since activation, remove it
                Logger.info(
                    "Project '{}' has not been updated for {} days".format(
                        project.name, INACTIVE_DAYS
                    ),
                    indent=indentSpace,
                )
                Logger.info(
                    "Setting Project '{}' to inactive".format(project.name),
                    indent=indentSpace,
                )
                project_service.updateProjectStatus(project.id, False)
                inactiveCount += 1
                continue

            # Check when the last task was completed
            lastDoneTask = DoneTasks[0]
            elapsed = datetime.datetime.now() - lastDoneTask.endDate
            if elapsed > datetime.timedelta(days=INACTIVE_DAYS):
                Logger.info(
                    "Project '{}' has not been updated for {} days".format(
                        project.name, INACTIVE_DAYS
                    ),
                    indent=indentSpace,
                )
                Logger.info(
                    "Setting Project '{}' to inactive".format(project.name),
                    indent=indentSpace,
                )
                project_service.updateProjectStatus(project.id, False)
                inactiveCount += 1

        if inactiveCount == 0:
            Logger.warn("No Active Projects are idle!", indent=indentSpace)
        else:
            Logger.warn(
                "{} Projects have been set to inactive".format(inactiveCount),
                indent=indentSpace,
            )

    def streakCommand(self, args=[]):
        DoneTasks = task_service.findAllTaskStatus(Status.DONE.value)
        if len(DoneTasks) == 0:
            Logger.warn("No Streaks")
            return
        today = 0
        highest = None
        days = {}
        for task in DoneTasks:
            if task.endDate.date() == datetime.datetime.now().date():
                today += 1
                continue

            dateString = task.endDate.date().isoformat()

            if dateString in days:
                days[dateString] += 1
            else:
                days[dateString] = 1

            if highest:
                if days[dateString] > days[highest]:
                    highest = dateString

            else:
                highest = dateString

        print("Streak")
        print("  Current: {} tasks".format(today))
        if highest != None:
            if days[highest] >= today:
                print("  Highest: {} tasks | {}".format(days[highest], highest))
                return

        print("  Highest: {} tasks | TODAY".format(today))

    def lastTaskCommand(self, args=[]):
        doneTasks = task_service.findAllTaskStatus(
            Status.DONE.value, orderBy=Task.endDate, desc=True
        )

        if len(doneTasks) == 0:
            print("Last done task: None")
            return

        print("Last done task: {}".format(convertDate(doneTasks[0].endDate)))

    def activateCommand(self, args=[]):

        for arg in args:
            try:
                complete = task_service.getCompletionForProject(arg)
                if complete == 1.0:
                    self.showScreen()
                    Logger.error("Project {} is already complete!".format(arg))
                    return

                update = project_service.updateProjectStatus(arg, True)
                if update:
                    self.showScreen()
                    Logger.success(
                        "Project {name} is set to active!".format(name=update.name)
                    )
            except:
                self.showScreen()
                Logger.error("Cannot update project " + arg)

    def deactivateCommand(self, args):

        for arg in args:
            try:
                update = project_service.updateProjectStatus(arg, False)
                if update:
                    self.showScreen()
                    Logger.success(
                        "Project {name} is set to inactive!".format(name=update.name)
                    )
            except:
                self.showScreen()
                Logger.error("Cannot update project " + arg)

    def openProjectCommand(self, args):
        project = project_service.getOneProject(args[0])

        projectView = ProjectViewCLI(project)

        close = projectView.run()

        if close:
            self.close()
        else:
            self.showScreen()

        return close
