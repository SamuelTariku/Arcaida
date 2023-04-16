from utils.simple_cli import *
from utils.log import Logger
from services import task_service
from models.task_model import Status
from colorama import Fore, Back, Style


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
            Command("reorder", self.reorderTaskCommand, 1),

        ])

    def createTaskCommand(self, args):
        newTask = task_service.createTask(" ".join(args), self.project)

        if(newTask):
            Logger.info("Task Name: {name}".format(name=newTask.name))
            Logger.success("Task is created!")

    def viewAllTaskCommand(self, args=None):
        tasks = task_service.getTasksByProject(self.project.id)

        print()
        for task in tasks:
            status = ""

            if(task.status == Status.BACKLOG.value):
                status = " "
            elif(task.status == Status.IN_PROGRESS.value):
                status = "*"
            elif(task.status == Status.DONE.value):
                status = "X"
            elif(task.status == Status.TESTING.value):
                status = "&"

            raw = "{num:>3}) {name:<38} [{status:<1}]".format(
                num=task.order,
                name=task.name,
                status=status
            )

            if(task.status == Status.IN_PROGRESS.value):
                print(Back.BLUE + raw, Back.RESET)
            elif(task.status == Status.DONE.value):
                print(Fore.LIGHTBLACK_EX + raw, Fore.RESET)
            else:
                print(raw)

        print()

    def renameTaskCommand(self, args):
        task = task_service.getTaskByOrder(self.project.id, args[0])
        update = task_service.updateTask(task, name=" ".join(args[1::]))

        if(update):
            Logger.info("Task Name: {name}".format(
                name=" ".join(args[1::])))
            Logger.success("Task name is updated!")

    def clearAllTaskCommand(self, args=None):
        clear = task_service.deleteTasksForProject(self.project.id)

        if(clear):
            Logger.info("Number of tasks deleted: {num}".format(
                num=clear
            ))
            Logger.success("All project tasks have been deleted!")

    def removeTaskCommand(self, args):
        task = task_service.getTaskByOrder(self.project.id, args[0])
        remove = task_service.deleteTask(task)

        if(remove):
            Logger.info("Number of tasks deleted: {num}".format(
                num=remove
            ))
            Logger.success("Task has been deleted!")

    def reorderTaskCommand(self, args):

        if(args[0] == "all"):
            task_service.reassignOrder(self.project.id)
            Logger.success("Tasks have been reordered")
            return

        reorder = task_service.updateOrder(self.project.id, args[0], args[1])
        if(reorder):
            Logger.success("Task has been moved!")
            self.viewAllTaskCommand()
