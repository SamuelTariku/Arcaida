from utils.simple_cli import *
from services.project import *
from utils.log import Logger


class baseCLI(CLI):

    def createProjectCommand(self, args):
        newProject = createProject(" ".join(args))
        if(newProject):
            Logger.info("Project Name: {name}".format(name=newProject.name))
            Logger.success("Project is created!")

    def viewAllProjectCommand(self, args=None):
        projects = getAllProject()
        for project in projects:
            print(str(project.id) + ") " + project.name)

    def renameProjectCommand(self, args):
        update = updateProjectName(
            args[0],
            " ".join(args[1::])
        )
        if(update):
            Logger.info("Project Name: {name}".format(
                name=" ".join(args[1::])))
            Logger.success("Project name is updated!")

    def clearAllProjectCommand(self, args=None):
        clear = deleteAllProject()
        if(clear):
            Logger.info("Number of projects deleted: {num}".format(
                num=clear
            ))
            Logger.success("All projects have been deleted!")

    def removeProjectCommand(self, args):
        remove = deleteOneProject(args[0])

        if(remove):
            Logger.info("Number of projects deleted: {num}".format(
                num=remove
            ))
            Logger.success("Project has been deleted!")

    def __init__(self) -> None:
        super().__init__()

        self.commands = self.generateCommandDict([
            Command("create", self.createProjectCommand, 1),
            Command("view", self.viewAllProjectCommand),
            Command("rename", self.renameProjectCommand, 2),
            Command("clear", self.clearAllProjectCommand),
            Command("remove", self.removeProjectCommand, 1),
        ])
