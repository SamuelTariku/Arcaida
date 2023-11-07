from services import deadline_service
from utils.simple_cli import *
from utils.deltaParser import calculateDate, convertDate


class DeadlineCLI(CLI):
    def __init__(self) -> None:
        super().__init__()
        self.prompt = "Deadlines"
        self.commands = self.generateCommandDict([
            Command("create", self.createDeadlineCommand, 1),
            Command("view", self.viewDeadlineCommand),
            Command("rename", self.renameDeadlineCommand, 2),
            Command("date", self.dateDeadlineCommand, 2),
            Command("clear", self.clearDeadlineCommand),
            Command("remove", self.removeDeadlineCommand, 1),
        ])

    def createDeadlineCommand(self, args):

        deadlineDate = calculateDate(args[0])

        newDeadline = deadline_service.createDeadline(
            name=" ".join(args[1::]), date=deadlineDate)

        if (newDeadline):
            Logger.info("Deadline Name: {name}".format(name=newDeadline.name))
            Logger.success("Deadline is created!")

    def viewDeadlineCommand(self, args=[]):

        deadlines = deadline_service.getAllDeadline()

        print()
        for deadline in deadlines:
            print("{id:>3}) {name:<38} {date}".format(
                id=deadline.id,
                name=deadline.name,
                date=convertDate(deadline.date)
            ))
        print()

    def renameDeadlineCommand(self, args):

        rename = deadline_service.updateDeadline(
            args[0], name=" ".join(args[1::]))

        if (rename):
            Logger.info("Deadline Name: {name}".format(
                name=" ".join(args[1::])))
            Logger.success("Deadline Name is updated!")

    def dateDeadlineCommand(self, args):

        deadlineDate = calculateDate(args[1])
        date = deadline_service.updateDeadline(
            args[0], date=deadlineDate)

        if (date):
            Logger.info("Deadline Date: {date}".format(
                date=convertDate(deadlineDate)))
            Logger.success("Deadline Date is updated!")

    def clearDeadlineCommand(self, args=[]):
        clear = deadline_service.deleteAllDeadline()

        if (clear):
            Logger.info("Number of deadlines deleted: {num}".format(
                num=clear
            ))
            Logger.success("All deadlines have been deleted!")

    def removeDeadlineCommand(self, args):

        remove = deadline_service.deleteOneDeadline(args[0])

        if (remove):
            Logger.info("Number of deadlines deleted: {num}".format(
                num=remove
            ))
            Logger.success("All deadlines have been deleted!")
