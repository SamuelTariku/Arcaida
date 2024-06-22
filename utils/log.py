from colorama import Fore, Back
from models.deadline_model import DeadlineStates
from models.task_model import Status
import datetime
import humanize
from art import tprint
import os

from utils.deltaParser import convertDate


class LogCollection:
    def __init__(self):
        self.logs = []  # Array of sets

    def execute(self):
        for logFunction, text in self.logs:
            logFunction(text)

    def add(self, logFunction, text):
        self.logs.append((logFunction, text))

    def success(self, text):
        self.logs.append((Logger.success, text))

    def error(self, text):
        self.logs.append((Logger.error, text))

    def warn(self, text):
        self.logs.append((Logger.warn, text))

    def heading(self, text):
        self.logs.append((Logger.heading, text))
        # tprint(indent + text, font="mini")

    def info(self, text):
        self.logs.append((Logger.info, text))

    def celebrate(self, text):
        self.logs.append((Logger.celebrate, text))


class Logger:

    def clear():
        os.system("cls" if os.name == "nt" else "clear")

    def header():
        print()
        # Generate header text
        print(Fore.CYAN, end="")
        # print("-" * 88)
        tprint("Arcadia", "shadow")
        # print(" " * 88)
        print(Fore.RESET, end="")

    def celebrate(text, indent=""):
        tprint(indent + text, font="straight")

    def success(text, indent=""):
        print(indent, Fore.LIGHTGREEN_EX + "[+]", text, Fore.RESET)

    def error(text, indent=""):
        print(indent, Fore.LIGHTRED_EX + "[!]", text, Fore.RESET)

    def warn(text, indent=""):
        print(indent, Fore.LIGHTBLACK_EX + "[*]", text, Fore.RESET)

    def heading(text, indent=""):
        print(indent, Fore.LIGHTBLUE_EX + "--", text.upper(), "--", Fore.RESET)
        # tprint(indent + text, font="mini")

    def info(text, indent=""):
        print(indent, Fore.LIGHTWHITE_EX + "[-]", text, Fore.RESET)

    def task(task, noHighlight=False, noIndex=False, byID=False):
        days = ""
        preColorSet = ""

        raw = "{num:>3}. {name:<53} {days}"
        noNumRaw = (" " * 5) + "{name:<53} {days}"

        if task.status == Status.BACKLOG.value:
            days = " "
        elif task.status == Status.IN_PROGRESS.value:
            if not noHighlight:
                preColorSet = Back.BLUE
            days = humanize.naturaldelta(datetime.datetime.now() - task.startDate)
        elif task.status == Status.DONE.value:
            preColorSet = Fore.LIGHTBLACK_EX
            days = humanize.naturaldelta(datetime.datetime.now() - task.endDate)
        elif task.status == Status.TESTING.value:
            preColorSet = Fore.MAGENTA
            days = "?"

        if noIndex:
            print(
                preColorSet
                + noNumRaw.format(
                    num=task.order if not byID else task.id, name=task.name, days=days
                ),
                Fore.RESET + Back.RESET,
            )
        else:
            print(
                preColorSet
                + raw.format(
                    num=task.order if not byID else task.id, name=task.name, days=days
                ),
                Fore.RESET + Back.RESET,
            )

    def project(project, complete, highlight=False):
        preColorSet = ""
        raw = "{num:>3}. {name:<26} |{progress:<30}| {complete:.0%}"

        # TODO: Validation for project name set max to 12 chars
        if not project.active:
            preColorSet = Fore.LIGHTBLACK_EX

        if highlight:
            preColorSet = Fore.CYAN

        print(
            preColorSet
            + raw.format(
                num=project.id,
                name=project.name,
                complete=complete,
                progress="|" * round(30 * complete),
            ),
            Fore.RESET + Back.RESET,
        )

    def deadline(deadline):
        preColorSet = ""
        raw = "{id:>3}. {name:<52} {date}"
        completedRaw = "{id:>3}) {name:<52} {text}"
        completed = False
        completedText = ""

        if deadline.state == DeadlineStates.PENDING.value:
            if deadline.date < datetime.datetime.now():
                preColorSet = Fore.RED
                completed = True
                completedText = "LATE"

        elif deadline.state == DeadlineStates.COMPLETE.value:
            preColorSet = Fore.BLACK
            completed = True
            completedText = "COMPLETE"

        if completed:
            print(
                preColorSet
                + completedRaw.format(
                    id=deadline.id, name=deadline.name, text=completedText
                ),
                Fore.RESET + Back.RESET,
            )
        else:
            print(
                preColorSet
                + raw.format(
                    id=deadline.id,
                    name=deadline.name,
                    date=convertDate(
                        deadline.date,
                    ),
                ),
                Fore.RESET,
            )
