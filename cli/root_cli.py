
import datetime
from cli.project_view_cli import ProjectViewCLI
from models.task_model import Status, Task
from peewee import DoesNotExist
from utils.deltaParser import convertDate
from utils.simple_cli import *
from cli.project_cli import ProjectCLI
from cli.deadline_cli import DeadlineCLI
from services import project_service, task_service
from utils.config import INACTIVE_DAYS
class BaseCLI(CLI):
    def __init__(self) -> None:
        super().__init__()
        self.commands = self.generateCommandDict([
            Command("projects", self.openProjectsCommand),
            Command("deadlines", self.openDeadlinesCommand),
            Command("open", self.openProjectCommand),
            Command("active", self.activeCommand),
            Command("view", self.viewCommand),
            Command("switch", self.switchCommand),
            Command("done", self.doneCommand),
            Command("edit", self.openDeadlinesCommand),
            Command("check-inactive", self.checkInactiveCommand),
            Command("streak", self.streakCommand),
            Command("last-task", self.lastTaskCommand),
            Command("activate", self.activateCommand, 1),
            Command("deactivate", self.deactivateCommand, 1),
        ])
        print()        
        # make a project inactive if last task was done before a month
        self.checkInactiveCommand()
        
        # show starting text
        print()
        self.lastTaskCommand()
        print()
        self.streakCommand()
        print()
        
        # TODO: the search for current task is done twice, replace with cli classes
        self.activeCommand()
        
        self.viewCommand()

    def openProjectsCommand(self, args=[]):
        projectCLI = ProjectCLI()

        close = projectCLI.run()
        if(close):
            self.close()
        return close

    def openDeadlinesCommand(self, args=[]):
        deadlineCLI = DeadlineCLI()

        close = deadlineCLI.run()
        if(close):
            self.close()
        return close

    def activeCommand(self, args=[]):
        activeProjects  = project_service.getActiveProjects()
        
        # get current task
        current = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)
        
        
        print("Active Projects")
        if(len(activeProjects) == 0):
            Logger.warn("No active projects set!")
            print()
            return
        
        if(len(current) == 0):
            highlight = None
        else:
            highlight = current[0].project.id
        
        print()
        for project in activeProjects:
            complete = task_service.getCompletionForProject(project.id)
            Logger.project(project, complete, highlight == project.id if highlight != None else False)
        print()
    
    def viewCommand(self, args=[]):
        current = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)
        
        print("Current Task")
        
        if(len(current) == 0):
            Logger.warn("There is no IN-PROGRESS task set")
            print()
            return
        elif(len(current) > 1):
            Logger.warn("There is more than one IN-PROGRESS task set!")
            Logger.warn("Something in the code has gone wrong!")
        print()
        complete = task_service.getCompletionForProject(current[0].project.id)
        Logger.project(current[0].project, complete)
        print("-" * 58)
        Logger.task(current[0], noHighlight=True, noOrder=True)
        print("" * 58)
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
        
        if(len(args) != 0):
            if(args[0] in ("project", "-p")):
                projectNumber = args[1] if len(args) > 1 else None
            elif(args[0] in ("task", "-t")):
                isCurrentProject = True
            elif(args[0] in ("random-project", "-rp")):
                isProjectRandom = True
            elif(args[0] in ("random-task", "-rt")):
                isCurrentProject = True
                isTaskRandom = True
            elif(args[0] in ("random", "-r")):
                isTaskRandom = True
                isProjectRandom = True
            elif(args[0].isnumeric()):
                projectNumber = int(args[0])
            else:
                Logger.error("Unknown {}: please check documentation".format(args[0]))
                return
        
        activeProjects  = project_service.getActiveProjects(random=isProjectRandom)
        
        if(len(activeProjects) == 0):
            Logger.warn("No active projects set!")
            print()
            return
        
        
        currentTask = None
        
        currentTasksQuery = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)    
        
        # Get next project
        if(projectNumber != None):
            try:
                nextProject = project_service.getOneProject(projectNumber)
                if(not nextProject.active):
                    Logger.error("Project is not active")
                    return
                if(len(currentTasksQuery) != 0):
                    currentTask = currentTasksQuery[0]
                    Logger.info("Setting Task '{}' to BACKLOG...".format(currentTask.name))
                    currentTask = task_service.updateStatus(currentTask, Status.BACKLOG.value)
                
            except DoesNotExist:
                Logger.error("No project with that id exists!")
                return
        else:
            if(len(currentTasksQuery) == 0):
                nextProject = activeProjects[0]
            else:
                currentTask = currentTasksQuery[0]
                
                # find the next project based on project id
                if(not isCurrentProject):    
                    nextProjectList = list(filter(lambda x: x.id > currentTask.project.id, list(activeProjects)))
                    if(len(nextProjectList) == 0):
                        nextProject = activeProjects[0]
                    else:
                        nextProject = nextProjectList[0]
                    Logger.info("Switching project to '{}'".format(nextProject.name))
                else:
                    nextProject = currentTask.project
                Logger.info("Setting Task '{}' to BACKLOG...".format(currentTask.name))
                currentTask = task_service.updateStatus(currentTask, Status.BACKLOG.value)
        
        todoTasksQuery = task_service.findAllTaskStatusForProject(Status.BACKLOG.value, nextProject.id, random=isTaskRandom)
        
        if(len(todoTasksQuery) == 0):
            Logger.error("There is an active project with no BACKLOG tasks")
            raise Exception("Active Project with no BACKLOG task")
        
        if(currentTask == None):
            firstTodo = todoTasksQuery[0]
        else:
            nextTodoList = list(filter(lambda x: x.id > currentTask.id, list(todoTasksQuery)))
            if(len(nextTodoList) == 0):
                firstTodo = todoTasksQuery[0]
            else:
                firstTodo = nextTodoList[0]
                
        Logger.info("Setting Task '{}' to IN-PROGRESS...".format(firstTodo.name))
        task_service.updateStatus(firstTodo, Status.IN_PROGRESS.value)
        Logger.success("Tasks have been updated!")
        print()
        self.viewCommand()
        
    
    def doneCommand(self, args=[]):
        currentTaskQuery = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)
        if(len(currentTaskQuery) == 0):
            Logger.error("No current task set!")
            return
        
        currentTask = currentTaskQuery[0]
        
        todoTasksQuery = task_service.findAllTaskStatusForProject(Status.BACKLOG.value, currentTask.project.id)
        
        print()
        print("Completion Time: {}".format(convertDate(currentTask.startDate, verbose=False)))
        print()
        
        Logger.info("Setting Task '{}' to DONE...".format(currentTask.name))
        task_service.updateStatus(currentTask, Status.DONE.value)
        
        if(len(todoTasksQuery) == 0):
            print()
            # self.viewCommand()
            print()
            Logger.success("All tasks in project completed!")
            Logger.celebrate("Project")
            Logger.celebrate("Completed!")
            Logger.info("Setting project to inactive...")
            project_service.updateProjectStatus(currentTask.project.id, False)
            Logger.success("Project set to inactive!")
            return
        
        firstTodo = todoTasksQuery[0]
        Logger.info("Setting Task '{}' to IN-PROGRESS...".format(firstTodo.name))
        task_service.updateStatus(firstTodo, Status.IN_PROGRESS.value)
        Logger.success("Tasks have been updated!")
        
        self.viewCommand()
        
    def checkInactiveCommand(self, args=[]):
        
        currentTaskQuery = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)
        
        currentTask = None
        if(len(currentTaskQuery) != 0):
            currentTask = currentTaskQuery[0]
            
        activeProjects = project_service.getActiveProjects()
        
        inactiveCount = 0
        
        
        for project in activeProjects:
            if(currentTask != None):
                if(currentTask.project.id == project.id):
                    # Check how long the current task hasn't been completed
                    elapsed = datetime.datetime.now() - currentTask.startDate
                    if(elapsed > datetime.timedelta(days=INACTIVE_DAYS)):
                        Logger.info("Project '{}' has not been updated for {} days".format(project.name, INACTIVE_DAYS))
                        
                        Logger.info("Setting Task '{}' to BACKLOG".format(currentTask.name))
                        task_service.updateStatus(currentTask, Status.BACKLOG.value)
                        
                        Logger.info("Setting Project '{}' to inactive".format(project.name))
                        project_service.updateProjectStatus(project.id, False)
                        inactiveCount += 1
                    continue
            
            DoneTasks = task_service.findAllTaskStatusForProject(Status.DONE.value, project.id, orderBy=Task.endDate, desc=True)
            
            if(len(DoneTasks) == 0):    
                # If project has no completed tasks, check how long its been active
                elapsed = datetime.datetime.now() - project.updated
                
                if(elapsed > datetime.timedelta(days=INACTIVE_DAYS)):
                    Logger.info("Project '{}' has not been updated for {} days".format(project.name, INACTIVE_DAYS))
                    Logger.info("Setting Project '{}' to inactive".format(project.name))
                    project_service.updateProjectStatus(project.id, False)
                    inactiveCount += 1
                continue
            
            # Check when the last task was completed
            lastDoneTask = DoneTasks[0]
            elapsed = datetime.datetime.now() - lastDoneTask.endDate
            if(elapsed > datetime.timedelta(days=INACTIVE_DAYS)):
                Logger.info("Project '{}' has not been updated for {} days".format(project.name, INACTIVE_DAYS))
                Logger.info("Setting Project '{}' to inactive".format(project.name))
                project_service.updateProjectStatus(project.id, False)
                inactiveCount += 1
        
        if(inactiveCount == 0):
            Logger.success("No Active Projects are idle!")
        else:
            Logger.warn("{} Projects have been set to inactive".format(inactiveCount))
        
    def streakCommand(self, args=[]):
        DoneTasks = task_service.findAllTaskStatus(Status.DONE.value)
        if(len(DoneTasks) == 0):
            Logger.info("No Streaks")
            return
        today = 0
        highest = None
        days = {}
        for task in DoneTasks:
            
            if(task.endDate.date() == datetime.datetime.now().date()):
                today += 1
                continue
            
            dateString = task.endDate.date().isoformat()
            
            if dateString in days:
                days[dateString] += 1
            else:
                days[dateString] = 1
            
            if(highest):    
                if(days[dateString] > days[highest]):
                    highest = dateString
                    
            else:
                highest = dateString
            
        print("Streak")
        print("  Current: {} tasks".format(today))
        if(days[highest] >= today):
            print("  Highest: {} tasks | {}".format(days[highest], highest))
        else:
            print("  Highest: {} tasks | TODAY".format(today))
        
    
    def lastTaskCommand(self, args=[]):
        doneTasks = task_service.findAllTaskStatus(Status.DONE.value, orderBy=Task.endDate, desc=True)
        
        if(len(doneTasks) == 0):
            print("Last done task: None")
            return
        
        print("Last done task: {}".format(convertDate(doneTasks[0].endDate)))
    
    def activateCommand(self, args=[]):
        for arg in args:
            try:
                complete = task_service.getCompletionForProject(arg)
                if(complete == 1.0):
                    Logger.error("Project {} is already complete!".format(arg))
                    return
                
                
                
                update = project_service.updateProjectStatus(arg, True)
                if(update):
                    Logger.success("Project {name} is set to active!".format(
                        name=update.name))
            except:
                Logger.error("Cannot update project " + arg)
    
    def deactivateCommand(self, args):
        for arg in args:
            try:
                update = project_service.updateProjectStatus(arg, False)
                if(update):
                    Logger.success("Project {name} is set to inactive!".format(
                        name=update.name))
            except:
                Logger.error("Cannot update project " + arg)
    
    def openProjectCommand(self, args):
        project = project_service.getOneProject(args[0])

        projectView = ProjectViewCLI(project)

        close = projectView.run()

        if(close):
            self.close()

        return close