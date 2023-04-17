from utils.simple_cli import *
from cli.project_cli import ProjectCLI


class BaseCLI(CLI):
    def __init__(self) -> None:
        super().__init__()
        self.commands = self.generateCommandDict([
            Command("projects", self.openProjectsCommand),
        ])

    def openProjectsCommand(self, args=None):
        projectCLI = ProjectCLI()

        close = projectCLI.run()
        if(close):
            self.close()
        return close
