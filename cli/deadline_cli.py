import datetime
from models.deadline_model import DeadlineStates
from services import deadline_service
from utils.simple_cli import *
from utils.deltaParser import calculateDate, convertDate


class DeadlineCLI(CLI):
    def __init__(self) -> None:
        super().__init__()
        self.prompt = "Deadlines"
        self.commands = self.generateCommandDict(
            [
                Command("create", self.createDeadlineCommand, 1),
                Command("view", self.viewDeadlineCommand),
                Command("rename", self.renameDeadlineCommand, 2),
                Command("update", self.updateDeadlineCommand, 2),
                Command("clear", self.clearDeadlineCommand),
                Command("remove", self.removeDeadlineCommand, 1),
            ]
        )

        self.showScreen()

    def showScreen(self):
        Logger.clear()
        Logger.header()
        Logger.heading("Deadlines")
        self.viewDeadlineCommand()

    def createDeadlineCommand(self, args=[]):
        deadlineDate = calculateDate(args[0])

        if deadlineDate == None:
            self.showScreen()
            Logger.error("Incorrect Datestring")
            return
        newDeadline = deadline_service.createDeadline(
            name=" ".join(args[1::]), date=deadlineDate
        )

        if newDeadline:
            self.showScreen()
            Logger.info("Deadline Name: {name}".format(name=newDeadline.name))
            Logger.success("Deadline is created!")

    def viewDeadlineCommand(self, args=[]):
        pendingDeadlines = deadline_service.findAllDeadlineState(
            DeadlineStates.PENDING.value
        )
        completedDeadlines = deadline_service.findAllDeadlineState(
            DeadlineStates.COMPLETE.value
        )

        print()
        for deadline in completedDeadlines:
            Logger.deadline(deadline)

        for deadline in pendingDeadlines:
            Logger.deadline(deadline)

        print()

    def renameDeadlineCommand(self, args=[]):
        rename = deadline_service.updateDeadline(args[0], name=" ".join(args[1::]))

        if rename:
            self.showScreen()
            Logger.info("Deadline Name: {name}".format(name=" ".join(args[1::])))
            Logger.success("Deadline Name is updated!")

    def updateDeadlineCommand(self, args=[]):
        deadlineDate = calculateDate(args[1])
        date = deadline_service.updateDeadline(args[0], date=deadlineDate)

        if date:
            self.showScreen()
            Logger.info("Deadline Date: {date}".format(date=convertDate(deadlineDate)))
            Logger.success("Deadline Date is updated!")

    def clearDeadlineCommand(self, args=[]):
        clear = deadline_service.deleteAllDeadline()

        if clear:
            self.showScreen()
            Logger.info("Number of deadlines deleted: {num}".format(num=clear))
            Logger.success("All deadlines have been deleted!")

    def removeDeadlineCommand(self, args=[]):
        remove = deadline_service.deleteOneDeadline(args[0])

        if remove:
            self.showScreen()
            Logger.info("Number of deadlines deleted: {num}".format(num=remove))
            Logger.success("All deadlines have been deleted!")
