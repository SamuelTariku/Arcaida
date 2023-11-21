import datetime
from utils.simple_cli import *
from utils.log import Logger
from utils.deltaParser import calculateDate, convertDate
from services import task_service, deadline_service, project_service
from models.task_model import Status

# from colorama import Fore, Back


class ProjectViewCLI(CLI):
    def __init__(self, project):
        super().__init__()

        self.project = project
        self.prompt = "~Project {}".format(project.name)
        self.commands = self.generateCommandDict(
            [
                Command("create", self.createTaskCommand, 1),
                Command("deadline", self.assignDeadlineCommand, 1),
                Command("bulk-create", self.bulkCreateTaskCommand),
                Command("view", self.viewTaskCommand),
                Command("status", self.statusTaskCommand, 2),
                Command("rename", self.renameTaskCommand, 2),
                Command("clear", self.clearAllTaskCommand),
                Command("remove", self.removeTaskCommand, 1),
                Command("reorder", self.reorderTaskCommand),
                Command("activate", self.activateCommand),
                Command("deactivate", self.deactivateCommand),
            ]
        )

        self.viewTaskCommand()

    def createTaskCommand(self, args):
        newTask = task_service.createTask(" ".join(args), self.project)

        if newTask:
            Logger.info("Task Name: {name}".format(name=newTask.name))
            Logger.success("Task is created!")

    def bulkCreateTaskCommand(self, args=[]):
        run = True
        Logger.warn('"wq" -- save and exit')
        Logger.warn('"q"  -- exit without saving')
        tasks = []

        print()
        while run:
            createQuery = input("--{num}> ".format(num=len(tasks)))
            if createQuery.lower() == "wq":
                run = False
            elif createQuery.lower() == "q":
                tasks = []
                run = False
            else:
                tasks.append(createQuery)
        print()

        created = 0
        for task in tasks:
            newTask = task_service.createTask(task, self.project)
            if newTask:
                created += 1

        Logger.info("Number of tasks created: {num}".format(num=created))
        if created != 0:
            Logger.success("Tasks have been created!")

    def viewTaskCommand(self, args=[]):
        doneTasks = task_service.findAllTaskStatusForProject(
            Status.DONE.value, self.project.id
        )
        backlogTasks = task_service.findAllTaskStatusForProject(
            Status.BACKLOG.value, self.project.id
        )
        currentTasks = task_service.findAllTaskStatusForProject(
            Status.IN_PROGRESS.value, self.project.id
        )
        if args == []:
            print()

            for task in backlogTasks:
                Logger.task(task)
            for task in currentTasks:
                Logger.task(task)
            for task in doneTasks:
                Logger.task(task)

            print()

    def statusTaskCommand(self, args):
        task = task_service.getTaskByOrder(self.project.id, args[0])

        if task == None:
            Logger.error("There is no task with that order")
            return

        status = None

        if args[1].lower() in ("backlog", "todo"):
            status = Status.BACKLOG.value

        elif args[1].lower() == "current":
            currentTasks = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)

            # Set IN-PROGRESS task to BACKLOG
            if len(currentTasks) >= 1:
                Logger.info("There can only be one IN-PROGRESS task")
                replace = input("replace? (y/N)>")

                if replace.lower() == "y":
                    # just in case idk
                    for currentTask in currentTasks:
                        currentTask.state = Status.BACKLOG.value
                        task_service.updateStatus(currentTask, Status.BACKLOG.value)
                else:
                    return
            # Set the project to active
            if not task.project.active:
                Logger.info("Set project to active...")
                project_service.updateProjectStatus(task.project.id, True)
                Logger.success("Project is active!")

            status = Status.IN_PROGRESS.value

        elif args[1].lower() == "test":
            status = Status.TESTING.value

        elif args[1].lower() == "done":
            todoTasks = task_service.findAllTaskStatusForProject(
                Status.BACKLOG.value, task.project.id
            )

            if task.status == Status.BACKLOG.value:
                todoTasksCount = todoTasks.count() - 1
            else:
                todoTasksCount = todoTasks.count()
                print()
                print(
                    "Completion Time: {}".format(
                        convertDate(task.startDate, verbose=False)
                    )
                )
                print()
                
            if todoTasksCount == 0:
                Logger.success("All tasks in project completed!")
                Logger.info("Setting project to inactive...")
                project_service.updateProjectStatus(task.project.id, False)
                Logger.success("Project set to inactive!")

            status = Status.DONE.value
        else:
            Logger.error("There is no such status")
            return

        update = task_service.updateStatus(task, status=status)
        if update:
            Logger.info("Task Name: {name}".format(name=task.name))
            Logger.success(
                "Task status is set to {status}!".format(status=Status(status).name)
            )

    def renameTaskCommand(self, args):
        task = task_service.getTaskByOrder(self.project.id, args[0])
        if task == None:
            Logger.error("There is no task with that order")
            return
        # err, update = task_service.renameTask(" ".join(args[1::]))
        task.name = " ".join(args[1::])

        try:
            task.save()
            Logger.info("Task Name: {name}".format(name=" ".join(args[1::])))
            Logger.success("Task name is updated!")
        except Exception as e:
            print(e)

    def clearAllTaskCommand(self, args=[]):
        clear = task_service.deleteTasksForProject(self.project.id)

        if clear:
            Logger.info("Number of tasks deleted: {num}".format(num=clear))
            Logger.success("All project tasks have been deleted!")

    def removeTaskCommand(self, args):
        task = task_service.getTaskByOrder(self.project.id, args[0])
        if task == None:
            Logger.error("There is no task with that order")
            return
        remove = task_service.deleteTask(task)

        if remove:
            Logger.info("Number of tasks deleted: {num}".format(num=remove))
            Logger.success("Task has been deleted!")

    def reorderTaskCommand(self, args=[]):
        task_service.reassignOrder(self.project.id)
        Logger.success("Tasks have been reordered")
        self.viewTaskCommand()

    def assignDeadlineCommand(self, args):
        # deadline 2 4 5 2
        tasks = task_service.getManyTask(self.project.id, args)

        if len(tasks) == 0:
            Logger.error("There is no task with that order")
            return
        # show deadlines viewer
        deadlines = deadline_service.getAllDeadline()

        if len(deadlines) == 0:
            Logger.error("No deadlines created!")
            return
        print()
        for deadline in deadlines:
            print(
                "{id:>3}) {name:<38} {date}".format(
                    id=deadline.id, name=deadline.name, date=convertDate(deadline.date)
                )
            )
        print()

        deadlineID = input("select>")

        if not deadlineID.isnumeric():
            Logger.error("deadline id incorrect!")
            return

        selectedDeadline = deadline_service.getOneDeadline(deadlineID)

        if selectedDeadline == None:
            Logger.error("There is no deadline with that id")
            return

        Logger.info("deadline " + selectedDeadline.name)
        # assign deadline to all passed tasks
        for task in tasks:
            task.deadline = selectedDeadline
            task.save()

    def activateCommand(self, args=[]):
        try:
            complete = task_service.getCompletionForProject(self.project.id)
            if complete == 1.0:
                Logger.error("Project {} is already complete!".format(self.project.id))
                return

            update = project_service.updateProjectStatus(self.project.id, True)
            if update:
                Logger.success(
                    "Project {name} is set to active!".format(name=update.name)
                )
        except:
            Logger.error("Cannot update project " + self.project.id)

    def deactivateCommand(self, args=[]):
        try:
            update = project_service.updateProjectStatus(self.project.id, False)
            if update:
                Logger.success(
                    "Project {name} is set to inactive!".format(name=update.name)
                )
        except:
            Logger.error("Cannot update project " + self.project.id)
