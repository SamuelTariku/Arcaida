from utils.simple_cli import *
from utils.log import Logger
from services import task_service


class ProjectCLI(CLI):

    def __init__(self, project):
        super().__init__()

        self.project = project
        self.prompt = "#Project {}> ".format(project.name)
        self.commands = self.generateCommandDict([
            Command("create", self.createTaskCommand, 1),
            Command("view", self.viewAllTaskCommand),
            Command("rename", self.renameTaskCommand, 2),
            Command("clear", self.clearAllTaskCommand),
            Command("remove", self.removeTaskCommand, 1),
        ])

    def createTaskCommand(self, args):
        newTask = task_service.createTask(" ".join(args), self.project)

        if(newTask):
            Logger.info("Task Name: {name}".format(name=newTask.name))
            Logger.success("Task is created!")

    def viewAllTaskCommand(self, args=None):
        tasks = task_service.getAllTasks()
        print()
        for task in tasks:
            raw = "{num:>3}) {name:<38} [ ]".format(
                num=task.id,
                name=task.name
            )
            print(raw)
        print()

    def renameTaskCommand(self, args):
        update = task_service.updateTask(args[0], name=" ".join(args[1::]))
        if(update):
            Logger.info("Task Name: {name}".format(
                name=" ".join(args[1::])))
            Logger.success("Task name is updated!")

    def clearAllTaskCommand(self, args):
        pass

    def removeTaskCommand(self, args):
        pass
