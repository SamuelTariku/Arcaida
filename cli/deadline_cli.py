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
                Command("date", self.dateDeadlineCommand, 2),
                Command("clear", self.clearDeadlineCommand),
                Command("remove", self.removeDeadlineCommand, 1),
                Command("activate", self.activateCommand, 1),
                Command("deactivate", self.deactivateCommand),
            ]
        )

    def createDeadlineCommand(self, args=[]):
        deadlineDate = calculateDate(args[0])

        newDeadline = deadline_service.createDeadline(
            name=" ".join(args[1::]), date=deadlineDate
        )

        if newDeadline:
            Logger.info("Deadline Name: {name}".format(name=newDeadline.name))
            Logger.success("Deadline is created!")

    def viewDeadlineCommand(self, args=[]):
        deadlines = deadline_service.getAllDeadline()
        print()
        for deadline in deadlines:
            Logger.deadline(deadline)
        print()

    def renameDeadlineCommand(self, args=[]):
        rename = deadline_service.updateDeadline(args[0], name=" ".join(args[1::]))

        if rename:
            Logger.info("Deadline Name: {name}".format(name=" ".join(args[1::])))
            Logger.success("Deadline Name is updated!")

    def dateDeadlineCommand(self, args=[]):
        deadlineDate = calculateDate(args[1])
        date = deadline_service.updateDeadline(args[0], date=deadlineDate)

        if date:
            Logger.info("Deadline Date: {date}".format(date=convertDate(deadlineDate)))
            Logger.success("Deadline Date is updated!")

    def clearDeadlineCommand(self, args=[]):
        clear = deadline_service.deleteAllDeadline()

        if clear:
            Logger.info("Number of deadlines deleted: {num}".format(num=clear))
            Logger.success("All deadlines have been deleted!")

    def removeDeadlineCommand(self, args=[]):
        remove = deadline_service.deleteOneDeadline(args[0])

        if remove:
            Logger.info("Number of deadlines deleted: {num}".format(num=remove))
            Logger.success("All deadlines have been deleted!")

    def activateCommand(self, args=[]):
        try:
            update = deadline_service.updateState(args[0], DeadlineStates.ACTIVE.value)

            if update:
                Logger.success(
                    "Deadline {name} is set to active!".format(name=update.name)
                )
        except Exception as e:
            Logger.error(e)

    def deactivateCommand(self, args=[]):
        # find the active deadline
        activeDeadlines = deadline_service.findAllDeadlineState(
            DeadlineStates.ACTIVE.value
        )

        try:
            # just in case
            for deadline in activeDeadlines:
                update = deadline_service.updateState(
                    deadline.id, DeadlineStates.PENDING.value
                )

            if update:
                Logger.success(
                    "Deadline {name} is set to active!".format(name=update.name)
                )
        except Exception as e:
            Logger.error(e)
