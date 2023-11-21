from colorama import Fore, Back
from models.deadline_model import DeadlineStates
from models.task_model import Status
import datetime
import humanize
from art import tprint

from utils.deltaParser import convertDate


class Logger:
    def celebrate(text):
        tprint(text, font="fuzzy")

    def success(text):
        print(Fore.GREEN + "[+]", text, Fore.RESET)

    def error(text):
        print(Fore.RED + "[!]", text, Fore.RESET)

    def warn(text):
        print(Fore.LIGHTYELLOW_EX + "[~]", text, Fore.RESET)

    def info(text):
        print(Fore.BLUE + "[.]", text, Fore.RESET)

    def task(task, noHighlight=False, noOrder=False):
        days = ""
        preColorSet = ""

        raw = "{num:>3}| {name:<42} {days}"
        noNumRaw = (" " * 5) + "{name:<42} {days}"

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

        if noOrder:
            print(
                preColorSet
                + noNumRaw.format(num=task.order, name=task.name, days=days),
                Fore.RESET + Back.RESET,
            )
        else:
            print(
                preColorSet + raw.format(num=task.order, name=task.name, days=days),
                Fore.RESET + Back.RESET,
            )

    def project(project, complete, highlight=False):
        preColorSet = ""
        raw = "{num:>3}| {name:<12} |{progress:<30}| {complete:.0%}"

        # TODO: Validation for project name set max to 12 chars
        if not project.active:
            preColorSet = Fore.LIGHTBLACK_EX

        if highlight:
            preColorSet = Fore.BLUE

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
        raw = "{id:>3}) {name:<38} {date}"
        completedRaw = "{id:>3}) {name:<38} {text}"
        completed = False
        completedText = ""

        if deadline.state == DeadlineStates.PENDING.value:
            pass

        elif deadline.state == DeadlineStates.ACTIVE.value:
            preColorSet = Fore.BLUE

        elif deadline.state == DeadlineStates.COMPLETE.value:
            preColorSet = Fore.BLACK
            completed = True
            completedText = "COMPLETE"

        elif deadline.state == DeadlineStates.LATE_COMPLETE.value:
            preColorSet = Fore.BLACK
            completed = True
            completedText = "LATE"

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
                        verbose=not (
                            (deadline.date - datetime.datetime.now())
                            > datetime.timedelta(hours=24)
                        ),
                    ),
                ),
                Fore.RESET,
            )
