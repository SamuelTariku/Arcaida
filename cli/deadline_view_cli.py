import datetime
import humanize
from peewee import DoesNotExist
from models.deadline_model import DeadlineStates
from models.task_model import Status
from utils.dateUtils import convertDate
from utils.simple_cli import *
from utils.log import Logger, LogCollection

from services import deadline_service, task_service, project_service


class DeadlineViewCLI(CLI):
    def __init__(self, deadline) -> None:
        super().__init__()

        self.deadline = deadline
        self.prompt = "~Deadline {}".format(deadline.id)
        self.commands = self.generateCommandDict(
            [
                Command("remove", self.unassignCommand, 1),
                Command("clear", self.clearCommand),
                Command("switch", self.switchCommand),
                Command("done", self.doneCommand),
            ]
        )
        self.showScreen()

    def showScreen(self):
        Logger.clear()
        Logger.header()
        Logger.heading("Deadline: {}".format(self.deadline.name))
        print()
        if self.deadline.state == DeadlineStates.PENDING.value:
            complete = deadline_service.getCompletion(self.deadline.id)
            print(
                " |{progress:<35}| {complete:<15.0%} Time Left: {time:>3}".format(
                    complete=complete,
                    progress="|" * round(35 * complete),
                    time=convertDate(
                        self.deadline.date,
                    ),
                )
            )
        else:
            print(
                " |{progress:<35}| {complete:<15.0%} Time Left: Completed".format(
                    complete=1.0,
                    progress="|" * 35,
                )
            )

        print()

        self.listTasks()
        print()

    def listTasks(self):

        tasks = deadline_service.getAllTasksForDeadline(self.deadline.id)

        for task in tasks:
            Logger.task(task, byID=True)

    def unassignCommand(self, args):
        # Expects a task id --> converts it to a task_deadline id
        remove = deadline_service.deleteOneTaskDeadline(self.deadline.id, args[0])
        self.showScreen()
        Logger.info("Number of tasks unassigned to deadline: {num}".format(num=remove))
        if remove:
            Logger.success("Tasks have been unassigned!")
            return

    def clearCommand(self, args=[]):
        clear = deadline_service.deleteAllTasksForDeadline(self.deadline.id)
        self.showScreen()
        Logger.info("Number of tasks unassigned to deadline: {num}".format(num=clear))
        if clear:
            Logger.success("Tasks have been unassigned!")
            return

    def switchCommand(self, args=[]):
        """
        switch [task_id]
        """

        logs = LogCollection()

        # Get current task
        nextTask = None

        # Sets next task
        if len(args) != 0:
            # TODO: Will need to change to the deadline id system later
            try:
                nextTask = task_service.getOneTask(args[0])
            except DoesNotExist:
                self.showScreen()
                logs.execute()
                Logger.error("No task with that id exists!")
                return
        else:
            todoDeadlineTasks = deadline_service.getTasksForDeadlineByStatus(
                self.deadline.id, Status.BACKLOG.value
            )

            if len(todoDeadlineTasks) == 0:
                logs.info("There are no more todo tasks!")
                self.showScreen()
                logs.execute()
                return

            firstTodo = todoDeadlineTasks[0]
            currentDeadlineTasks = deadline_service.getTasksForDeadlineByStatus(
                self.deadline.id, Status.IN_PROGRESS.value
            )
            # If current task not in deadline, set the first task to current
            if len(currentDeadlineTasks) == 0:
                nextTask = firstTodo
            else:
                # If current task is in deadline, find the next task after that and replace that one
                # check if the current task is in deadline
                nextTaskList = list(
                    filter(
                        lambda x: x.id > currentDeadlineTasks[0].id,
                        list(todoDeadlineTasks),
                    )
                )

                if len(nextTaskList) == 0:
                    nextTask = firstTodo
                else:
                    nextTask = nextTaskList[0]

        if self.deadline.state == DeadlineStates.COMPLETE.value:
            self.showScreen()
            Logger.info("Deadline is already completed")
            reactivate = input("reactivate? (y/N)>")

            if reactivate.lower() == "y":
                deadline_service.updateState(
                    self.deadline.id, DeadlineStates.PENDING.value
                )
            else:
                self.showScreen()
                return

        currentTaskQuery = task_service.findAllTaskStatus(Status.IN_PROGRESS.value)

        if len(currentTaskQuery) >= 1:
            currentTask = currentTaskQuery[0]
            logs.info("Setting Task '{}' to BACKLOG...".format(currentTask.name))
            task_service.updateStatus(currentTask, Status.BACKLOG.value)

        logs.info("Setting Task '{}' to IN_PROGRESS...".format(nextTask.name))
        task_service.updateStatus(nextTask, Status.IN_PROGRESS.value)

        if not nextTask.project.active:
            logs.info("Set project '{}' to active...".format(nextTask.project.name))
            project_service.updateProjectStatus(nextTask.project.id, True)

        self.showScreen()
        logs.execute()

    def doneCommand(self, args=[]):

        logs = LogCollection()

        currentDeadlineTasks = deadline_service.getTasksForDeadlineByStatus(
            self.deadline.id, Status.IN_PROGRESS.value
        )
        if len(currentDeadlineTasks) == 0:
            self.showScreen()
            logs.execute()
            Logger.error("No task set to current in deadline")
            return

        currentTask = currentDeadlineTasks[0]

        todoDeadlineTasks = deadline_service.getTasksForDeadlineByStatus(
            self.deadline.id, Status.BACKLOG.value
        )
        logs.info(
            "Completion Time: {}".format(
                humanize.naturaldelta(datetime.datetime.now() - currentTask.startDate)
            ),
        )
        logs.info("Setting Task '{}' to DONE...".format(currentTask.name))
        task_service.updateStatus(currentTask, Status.DONE.value)

        # Set the project that the task is from to inactive if the project is completed
        currentTaskProject = task_service.findAllTaskStatusForProject(
            Status.BACKLOG.value, currentTask.project.id
        )
        if len(currentTaskProject) == 0:
            project_service.updateProjectStatus(currentTask.project.id, False)
            logs.success(
                "All tasks in project '{}' completed".format(currentTask.project.name)
            )

        # Set the deadline to complete if all tasks are done
        if len(todoDeadlineTasks) == 0:
            self.deadline = deadline_service.updateState(
                self.deadline.id, DeadlineStates.COMPLETE.value
            )
            logs.success("All tasks in deadline completed!")
            # logs.celebrate("Project Completed")

            self.showScreen()
            logs.execute()
            return

        firstTodo = todoDeadlineTasks[0]
        logs.info("Setting Task '{}' to IN-PROGRESS...".format(firstTodo.name))
        task_service.updateStatus(firstTodo, Status.IN_PROGRESS.value)

        self.showScreen()
        logs.execute()
