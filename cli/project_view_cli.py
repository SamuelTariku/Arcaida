from utils.simple_cli import *
from utils.log import Logger
from services import task_service
from models.task_model import Status
from colorama import Fore, Back


class ProjectViewCLI(CLI):

    def __init__(self, project):
        super().__init__()

        self.project = project
        self.prompt = "#Project {}> ".format(project.name)
        self.commands = self.generateCommandDict([
            Command("create", self.createTaskCommand, 1),
            Command("bulk-create", self.bulkCreateTaskCommand),
            Command("view", self.viewTaskCommand),
            Command("status", self.statusTaskCommand, 2),
            Command("status-next", self.statusNextTaskCommand),
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

        if(task == None):
            Logger.error("There is no task with that order")
            return
        status = None
        if(args[1].lower() == "backlog"):
            status = Status.BACKLOG.value
        elif(args[1].lower() == "current"):
            currentTasks = task_service.findAllTaskStatusForProject(
                Status.IN_PROGRESS.value, self.project.id)

            if(len(currentTasks) >= 1):
                Logger.error("There can only be one IN-PROGRESS task")
                return

            status = Status.IN_PROGRESS.value

        elif(args[1].lower() == "test"):
            status = Status.TESTING.value

        elif(args[1].lower() == "done"):
            status = Status.DONE.value

        update = task_service.updateTask(task, status=status)
        if(update):
            Logger.info("Task Name: {name}".format(
                name=task.name))
            Logger.success("Task status is set to {status}!".format(
                status=Status(status).name))

    def statusNextTaskCommand(self, args=None):

        inProgress = task_service.findAllTaskStatusForProject(
            Status.IN_PROGRESS.value, self.project.id)

        # If there are no tasks in progress
        if(len(inProgress) == 0):
            backlogTasks = task_service.findAllTaskStatusForProject(
                Status.BACKLOG.value, self.project.id)

            if(len(backlogTasks) == 0):
                Logger.error("There are no remaining tasks")
                return

            firstTask = backlogTasks[0]

            task_service.updateTask(firstTask, status=Status.IN_PROGRESS.value)

            Logger.info("Task Name: {name}".format(
                name=firstTask.name))
            Logger.success("Task status is set to {status}!".format(
                status=Status.IN_PROGRESS.name))

            return

        currentTask = inProgress[0]

        nextTask = task_service.getTaskByOrder(
            self.project.id, currentTask.order + 1)

        updateCurrentTask = task_service.updateTask(
            currentTask, status=Status.DONE.value)

        if(updateCurrentTask == None):
            Logger.error("Cannot update currentTask")
            return

        updateNextTask = task_service.updateTask(
            nextTask, status=Status.IN_PROGRESS.value)

        if(updateNextTask == None):
            Logger.error("Cannot update currentTask")
            return

        Logger.info("IN-PROGRESS Task Name: {name}".format(
            name=currentTask.name))
        Logger.success("Task status is set to {status}!".format(
            status=Status.DONE.name))
        Logger.info("Next Task Name: {name}".format(
            name=nextTask.name))
        Logger.success("Task status is set to {status}!".format(
            status=Status.IN_PROGRESS.name))

    def renameTaskCommand(self, args):
        task = task_service.getTaskByOrder(self.project.id, args[0])
        if(task == None):
            Logger.error("There is no task with that order")
            return
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
        if(task == None):
            Logger.error("There is no task with that order")
            return
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
