from utils.simple_cli import *
from cli.project_cli import ProjectCLI
from cli.deadline_cli import DeadlineCLI


class BaseCLI(CLI):
    def __init__(self) -> None:
        super().__init__()
        self.commands = self.generateCommandDict([
            Command("projects", self.openProjectsCommand),
            Command("deadlines", self.openDeadlinesCommand),
            Command("edit", self.openDeadlinesCommand),
            
        ])
        
        # show starting text
        print()
        print("Show Current Streak: | Show Highest Streak: ")
        print("Show active projects")
        print("Show ")

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
    
    
    def viewCommand(self, args=None):
        pass
