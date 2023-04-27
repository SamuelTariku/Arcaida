from services import deadline_service
from utils.simple_cli import *
from utils.deltaParser import calculateDate


class DeadlineCLI(CLI):
    def __init__(self) -> None:
        super().__init__()
        self.prompt = "Deadlines"
        self.commands = self.generateCommandDict([
            Command("create", self.createDeadlineCommand, 1),
        ])

    def createDeadlineCommand(self, args):

        deadlineDate = calculateDate(args[0])

        newDeadline = deadline_service.createDeadline(
            name=" ".join(args[1::]), date=deadlineDate)

        if(newDeadline):
            Logger.info("Deadline Name: {name}".format(name=newDeadline.name))
            Logger.success("Deadline is created!")
