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
            Command("edit", self.openDeadlinesCommand),
        ])
        
        # show starting text
        print()
        print("Last task done: 4 days ago")
        
        print("Current Streak: | Highest Streak: ")
        print()
        print("Active Projects")
        self.activeCommand()
        
        print("Current Task")
        

    def openProjectsCommand(self, args=None):
        projectCLI = ProjectCLI()

        close = projectCLI.run()
        if(close):
            self.close()
        return close

    def openDeadlinesCommand(self, args=None):
        deadlineCLI = DeadlineCLI()

        close = deadlineCLI.run()
        if(close):
            self.close()
        return close

    def activeCommand(self, args=None):
        activeProjects  = project_service.getActiveProjects()
        current = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)
        if(len(current) == 0):
            highlight = None
        else:
            highlight = current[0].project.id
            
        print()
        for project in activeProjects:
            complete = task_service.getCompletionForProject(project.id)
            Logger.project(project, complete, highlight == project.id if highlight != None else False)
        print()
    
    