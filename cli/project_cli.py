from utils.simple_cli import *
from services import project_service, task_service
from utils.log import Logger
from colorama import Fore
from cli.project_view_cli import ProjectViewCLI


class ProjectCLI(CLI):

    def __init__(self) -> None:
        super().__init__()
        self.prompt = "Projects"
        self.commands = self.generateCommandDict([
            Command("create", self.createProjectCommand, 1),
            Command("view", self.viewAllProjectCommand),
            Command("rename", self.renameProjectCommand, 2),
            Command("clear", self.clearAllProjectCommand),
            Command("remove", self.removeProjectCommand, 1),
            Command("open", self.openProjectCommand, 1),
            Command("open", self.openProjectCommand, 1),
            Command("active", self.activeProjectCommand, 1),
            Command("inactive", self.inactiveProjectCommand, 1),
        ])
        
        self.viewAllProjectCommand()

    def createProjectCommand(self, args):
        newProject = project_service.createProject(" ".join(args))
        if(newProject):
            Logger.info("Project Name: {name}".format(name=newProject.name))
            Logger.success("Project is created!")

    # TODO: add filters
    def viewAllProjectCommand(self, args=[]):
        projects = project_service.getAllProject()
        
        print()
        for project in projects:
            complete = task_service.getCompletionForProject(project.id)
            Logger.project(project, complete)
        print()

    def renameProjectCommand(self, args):
        try:
            update = project_service.updateProjectName(
                args[0],
                " ".join(args[1::])
            )
            
            if(update):
                Logger.success("Project {name} is updated!".format(
                        name=update.name))
        except Exception as err:
            Logger.error("Cannot update project!")
            print(err)
        

    def clearAllProjectCommand(self, args=[]):
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

        projectView = ProjectViewCLI(project)

        close = projectView.run()

        if(close):
            self.close()

        return close
    
    def activeProjectCommand(self, args):
        for arg in args:
            try:
                update = project_service.updateProjectStatus(arg, True)
                if(update):
                    Logger.success("Project {name} is set to active!".format(
                        name=update.name))
            except:
                Logger.error("Cannot update project " + arg)
            
    def inactiveProjectCommand(self, args):
        for arg in args:
            try:
                update = project_service.updateProjectStatus(arg, False)
                if(update):
                    Logger.success("Project {name} is set to inactive!".format(
                        name=update.name))
            except:
                Logger.error("Cannot update project " + arg)