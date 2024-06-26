from utils.deltaParser import convertDate
from utils.simple_cli import *
from utils.log import Logger, LogCollection

from services import deadline_service


class DeadlineViewCLI(CLI):
    def __init__(self, deadline) -> None:
        super().__init__()

        self.deadline = deadline
        self.prompt = "~Deadline {}".format(deadline.id)
        self.commands = self.generateCommandDict(
            [
                Command("remove", self.unassignCommand, 1),
                Command("clear", self.clearCommand),
            ]
        )
        self.showScreen()

    def showScreen(self):
        Logger.clear()
        Logger.header()
        Logger.heading("Deadline: {}".format(self.deadline.name))

        complete = deadline_service.getCompletion(self.deadline.id)
        print()
        print(
            " |{progress:<35}| {complete:<15.0%} Time Left: {time:>3}".format(
                complete=complete,
                progress="|" * round(35 * complete),
                time=convertDate(
                    self.deadline.date,
                ),
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

    def switchCommand(self):
        pass

    def doneCommand(self):
        pass
