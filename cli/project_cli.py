from utils.simple_cli import *
from utils.log import Logger
from services import task_service
from models.task_model import Status
from colorama import Fore, Back


class ProjectCLI(CLI):

    def __init__(self, project):
        super().__init__()

        self.project = project
        self.prompt = "#Project {}> ".format(project.name)
        self.commands = self.generateCommandDict([
            Command("create", self.createTaskCommand, 1),
            Command("bulk-create", self.bulkCreateTaskCommand),
            Command("view", self.viewTaskCommand),
            Command("status", self.statusTaskCommand, 2),
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

    def bulkCreateTaskCommand(self, args=None):
        run = True
        Logger.warn("\"wq\" -- save and exit")
        Logger.warn("\"q\"  -- exit without saving")
        tasks = []

        print()
        while run:
            createQuery = input("--{num}> ".format(num=len(tasks)))
            if(createQuery.lower() == "wq"):
                run = False
            elif(createQuery.lower() == "q"):
                tasks = []
                run = False
            else:
                tasks.append(createQuery)
        print()

        created = 0
        for task in tasks:
            newTask = task_service.createTask(task, self.project)
            if(newTask):
                created += 1

        Logger.info("Number of tasks created: {num}".format(num=created))
        if(created != 0):
            Logger.success("Tasks have been created!")

    def viewTaskCommand(self, args=None):
        tasks = task_service.getTasksByProject(self.project.id)

        print()
        for task in tasks:
            status = ""
            preColorSet = ""
            postColorSet = ""

            raw = "{num:>3}) {name:<38} [{status:<1}]"
            if(task.status == Status.BACKLOG.value):
                status = " "
            elif(task.status == Status.IN_PROGRESS.value):
                preColorSet = Back.BLUE
                postColorSet = Back.RESET
                status = "o"
            elif(task.status == Status.DONE.value):
                preColorSet = Fore.LIGHTBLACK_EX
                postColorSet = Fore.RESET
                status = "x"
            elif(task.status == Status.TESTING.value):
                preColorSet = Fore.MAGENTA
                postColorSet = Fore.RESET
                status = "T"

            print(preColorSet + raw.format(
                num=task.order,
                name=task.name,
                status=status
            ), postColorSet)

        print()

    def statusTaskCommand(self, args):
        task = task_service.getTaskByOrder(self.project.id, args[0])
        status = None
        if(args[1].lower() == "backlog"):
            status = Status.BACKLOG.value
        elif(args[1].lower() == "current"):
            # TODO: make it so that there can only be one in-progress task
            status = Status.IN_PROGRESS.value

        elif(args[1].lower() == "test"):
            status = Status.TESTING.value

        elif(args[1].lower() == "done"):
            status = Status.DONE.value

        update = task_service.updateTask(task, status=status)
        if(update):
            Logger.info("Task Name: {name}".format(
                name=task.name))
            Logger.success("Task name is updated!")

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
            self.viewTaskCommand()
