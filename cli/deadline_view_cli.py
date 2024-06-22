from utils.deltaParser import convertDate
from utils.simple_cli import *
from utils.log import Logger, LogCollection

from services import deadline_service


class DeadlineViewCLI(CLI):
    def __init__(self, deadline) -> None:
        super().__init__()

        self.deadline = deadline
        self.prompt = "~Deadline {}".format(deadline.id)
        self.commands = self.generateCommandDict([])
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

        tasks = deadline_service.getAllTaskDeadlines(self.deadline.id)

        for task in tasks:
            Logger.task(task, byID=True)
            
    
    
