from models.task_model import Status
from utils.simple_cli import *
from cli.project_cli import ProjectCLI
from cli.deadline_cli import DeadlineCLI
from services import project_service, task_service

class BaseCLI(CLI):
    def __init__(self) -> None:
        super().__init__()
        self.commands = self.generateCommandDict([
            Command("projects", self.openProjectsCommand),
            Command("deadlines", self.openDeadlinesCommand),
            Command("active", self.activeCommand),
            Command("view", self.viewCommand),
            Command("switch", self.switchCommand),
            Command("done", self.doneCommand),
            Command("edit", self.openDeadlinesCommand),
        ])
        
        # show starting text
        print()
        print("Last task done: 4 days ago")
        
        print("Current Streak: | Highest Streak: ")
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
                default                 change project
                -p  project             change project
                -t  task                change task within current project
                -rp random-project      change to random project
                -rt random-task         change to random task within current project
                -r random               change to random task within random project
        """
        
        isCurrentProject = False
        isProjectRandom = False
        isTaskRandom = False
        
        if(len(args) != 0):
            if(args[0] in ("project", "-p")):
                pass
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
            else:
                Logger.error("Unknown {}: please check documentation".format(args[0]))
        
        print(isCurrentProject, isProjectRandom, isTaskRandom)
        activeProjects  = project_service.getActiveProjects(random=isProjectRandom)
        
        if(len(activeProjects) == 0):
            Logger.warn("No active projects set!")
            print()
            return
        
        currentTasksQuery = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)
        currentTask = None
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
        current = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)
        if(len(current) == 0):
            Logger.error("No current task set!")
            return
        
        todoTasksQuery = task_service.findAllTaskStatusForProject(Status.BACKLOG.value, current[0].project.id)
        
        Logger.info("Setting Task '{}' to DONE...".format(current[0].name))
        task_service.updateStatus(current[0], Status.DONE.value)
        
        
        if(len(todoTasksQuery) == 0):
            print()
            # self.viewCommand()
            print()
            Logger.success("All tasks in project completed!")
            Logger.celebrate("Project")
            Logger.celebrate("Completed!")
            Logger.info("Setting project to inactive...")
            project_service.updateProjectStatus(current[0].project.id, False)
            Logger.success("Project set to inactive!")
            return
        
        firstTodo = todoTasksQuery[0]
        Logger.info("Setting Task '{}' to IN-PROGRESS...".format(firstTodo.name))
        task_service.updateStatus(firstTodo, Status.IN_PROGRESS.value)
        Logger.success("Tasks have been updated!")
        
        self.viewCommand()
        
        