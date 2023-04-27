from colorama import Fore, Back
from models.task_model import Status

class Logger:

    def success(text):
        print(Fore.GREEN + "[+]", text, Fore.RESET)

    def error(text):
        print(Fore.RED + "[!]", text, Fore.RESET)

    def warn(text):
        print(Fore.YELLOW + "[-]", text, Fore.RESET)

    def info(text):
        print(Fore.BLUE + "[*]", text, Fore.RESET)

    def task(task):
        status = ""
        preColorSet = ""
        postColorSet = ""
        raw = "{num:>3}) {name:<38} [{status:<1}]"
        if(task.status == Status.BACKLOG.value):
            status = " "
        elif(task.status == Status.IN_PROGRESS.value):
            preColorSet = Back.BLUE
            postColorSet = Back.RESET
            status = "o"
        elif(task.status == Status.DONE.value):
            preColorSet = Fore.LIGHTBLACK_EX
            postColorSet = Fore.RESET
            status = "x"
        elif(task.status == Status.TESTING.value):
            preColorSet = Fore.MAGENTA
            postColorSet = Fore.RESET
            status = "T"

        print(preColorSet + raw.format(
            num=task.order,
            name=task.name,
            status=status
        ), postColorSet)
