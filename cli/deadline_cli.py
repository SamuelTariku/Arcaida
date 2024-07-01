from peewee import DoesNotExist
import humanize
import datetime
from cli.deadline_view_cli import DeadlineViewCLI
from models.deadline_model import DeadlineStates
from services import deadline_service
from utils.simple_cli import *
from utils.dateUtils import calculateDate, convertDate, parse_time


class DeadlineCLI(CLI):
    def __init__(self) -> None:
        super().__init__()
        self.prompt = "Deadlines"
        self.commands = self.generateCommandDict(
            [
                Command("create", self.createDeadlineCommand, 1),
                Command("open", self.openDeadlineCommand, 1),
                Command("rename", self.renameDeadlineCommand, 2),
                Command("update", self.updateDeadlineCommand, 2),
                Command("delay", self.delayDeadlineCommand, 2),
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

    def openDeadlineCommand(self, args):
        try:
            deadline = deadline_service.getOneDeadline(args[0])
        except DoesNotExist:
            self.showScreen()
            Logger.error("Deadline doesn't exist")
            return

        deadlineView = DeadlineViewCLI(deadline)

        close = deadlineView.run()

        if close:
            self.close()
        else:
            self.showScreen()

        return close

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

        checkFixed = deadline_service.checkFixedDeadline(args[0])
        if not checkFixed:
            self.showScreen()
            Logger.error("Fixed Deadline cannot be modified")
            return

        rename = deadline_service.updateDeadline(args[0], name=" ".join(args[1::]))

        if rename:
            self.showScreen()
            Logger.info("Deadline Name: {name}".format(name=" ".join(args[1::])))
            Logger.success("Deadline Name is updated!")

    def updateDeadlineCommand(self, args=[]):

        checkFixed = deadline_service.checkFixedDeadline(args[0])

        if not checkFixed:
            self.showScreen()
            Logger.error("Fixed Deadline cannot be modified")
            return
        deadlineDate = calculateDate(args[1])

        try:
            date = deadline_service.updateDeadline(args[0], date=deadlineDate)
        except DoesNotExist:
            self.showScreen()
            Logger.error("Project doesn't exist")
            return

        if date:
            self.showScreen()
            Logger.info("Deadline Date: {date}".format(date=convertDate(deadlineDate)))
            Logger.success("Deadline Date is updated!")

    def delayDeadlineCommand(self, args=[]):

        checkFixed = deadline_service.checkFixedDeadline(args[0])

        if not checkFixed:
            self.showScreen()
            Logger.error("Fixed Deadline cannot be modified")
            return
        deadlineDelay = parse_time(args[1])
        try:
            newDeadline = deadline_service.delayDeadline(
                args[0], timeDelta=deadlineDelay
            )
        except DoesNotExist:
            self.showScreen()
            Logger.error("Project doesn't exist")
            return
        
        if newDeadline:
            self.showScreen()
            Logger.info(
                "Deadline Date: {date}".format(
                    date=humanize.naturaltime(newDeadline.date)
                )
            )
            Logger.success("Deadline Date is updated!")
        else:
            self.showScreen()
            Logger.error("Unable to update deadline")

    def clearDeadlineCommand(self, args=[]):
        clear = deadline_service.deleteAllDeadline()

        self.showScreen()
        if clear:
            Logger.info("Number of deadlines deleted: {num}".format(num=clear))
            Logger.success("All deadlines have been deleted!")
        else:
            Logger.info("Number of deadlines deleted: {num}".format(num=clear))

    def removeDeadlineCommand(self, args=[]):
        checkFixed = deadline_service.checkFixedDeadline(args[0])
        if not checkFixed:
            self.showScreen()
            Logger.error("Fixed Deadline cannot be modified")
            return

        remove = deadline_service.deleteOneDeadline(args[0])

        if remove:
            self.showScreen()
            Logger.info("Number of deadlines deleted: {num}".format(num=remove))
            Logger.success("All deadlines have been deleted!")
