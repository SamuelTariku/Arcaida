from utils.simple_cli import *
from controller.project import *
from utils.log import Logger


class baseCLI(CLI):

    def createCommand(self, args):
        newProject = createProject(" ".join(args))
        if(newProject):
            Logger.info("Project Name: {name}".format(name=newProject.name))
            Logger.success("Project is created!")

    def __init__(self) -> None:
        super().__init__()

        self.commands = self.generateCommandDict([
            Command("exit", self.close),
            Command("create", self.createCommand, 1)
        ])
