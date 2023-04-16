from utils.simple_cli import *
from services import project_service
from utils.log import Logger

from cli.project_cli import ProjectCLI


class BaseCLI(CLI):

    def __init__(self) -> None:
        super().__init__()

        self.commands = self.generateCommandDict([
            Command("create", self.createProjectCommand, 1),
            Command("view", self.viewAllProjectCommand),
            Command("rename", self.renameProjectCommand, 2),
            Command("clear", self.clearAllProjectCommand),
            Command("remove", self.removeProjectCommand, 1),
            Command("open", self.openProjectCommand, 1)
        ])

    def createProjectCommand(self, args):
        newProject = project_service.createProject(" ".join(args))
        if(newProject):
            Logger.info("Project Name: {name}".format(name=newProject.name))
            Logger.success("Project is created!")

    # TODO: add filters 
    def viewAllProjectCommand(self, args=None):
        projects = project_service.getAllProject()
        print()
        for project in projects:
            print(" ", str(project.id) + ") " + project.name)
        print()

    def renameProjectCommand(self, args):
        update = project_service.updateProjectName(
            args[0],
            " ".join(args[1::])
        )
        if(update):
            Logger.info("Project Name: {name}".format(
                name=" ".join(args[1::])))
            Logger.success("Project name is updated!")

    def clearAllProjectCommand(self, args=None):
        clear = project_service.deleteAllProject()
        if(clear):
            Logger.info("Number of projects deleted: {num}".format(
                num=clear
            ))
            Logger.success("All projects have been deleted!")

    def removeProjectCommand(self, args):
        remove = project_service.deleteOneProject(args[0])

        if(remove):
            Logger.info("Number of projects deleted: {num}".format(
                num=remove
            ))
            Logger.success("Project has been deleted!")

    def openProjectCommand(self, args):
        project = project_service.getOneProject(args[0])

        projectCLI = ProjectCLI(project)
        close = projectCLI.run()

        if(close):
            self.close()
