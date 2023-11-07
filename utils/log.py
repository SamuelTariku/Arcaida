from colorama import Fore, Back
from models.task_model import Status
import datetime
import humanize
from art import tprint
class Logger:
    def celebrate(text):
        tprint(text, font="fuzzy")
    def success(text):
        print(Fore.GREEN + "[+]", text, Fore.RESET)

    def error(text):
        print(Fore.RED + "[!]", text, Fore.RESET)

    def warn(text):
        print(Fore.YELLOW + "[?]", text, Fore.RESET)

    def info(text):
        print(Fore.BLUE + "[.]", text, Fore.RESET)

    def task(task, noHighlight=False, noOrder=False):
        days = ""
        preColorSet = ""
        postColorSet = ""
        
        raw = "{num:>3}| {name:<42} {days}"
        noNumRaw = (" " * 5) + "{name:<42} {days}"
         
        if(task.status == Status.BACKLOG.value):
            days = " "
        elif(task.status == Status.IN_PROGRESS.value):
            if(not noHighlight):
                preColorSet = Back.BLUE
                postColorSet = Back.RESET
            days = humanize.naturaldelta(datetime.datetime.utcnow() - task.startDate)
        elif(task.status == Status.DONE.value):
            preColorSet = Fore.LIGHTBLACK_EX
            postColorSet = Fore.RESET
            days = humanize.naturaldelta(datetime.datetime.utcnow() - task.endDate)
        elif(task.status == Status.TESTING.value):
            preColorSet = Fore.MAGENTA
            postColorSet = Fore.RESET
            days = "?"
        
        if(noOrder):
            print(preColorSet + noNumRaw.format(
                num=task.order,
                name=task.name,
                days=days
            ), postColorSet)
        else:
            print(preColorSet + raw.format(
                num=task.order,
                name=task.name,
                days=days
            ), postColorSet)
    
    def project(project, complete, highlight=False):
        preColorSet = ""
        postColorSet = ""
        
        preProgressSet = ""
        postProgressSet  = ""
        
        preBarSet = ""
        postBarSet  = ""
        # TODO: Validation for project name set max to 12 chars
        if(not project.active):
            preColorSet = Fore.LIGHTBLACK_EX
            postColorSet = Fore.RESET
            
        if(highlight):
            preColorSet = Fore.BLUE
            postColorSet = Fore.RESET
            
            preBarSet = Back.BLUE
            postBarSet = Back.RESET
            
        raw = "{num:>3}| {name:<12} |{progress:<30}| {complete:.0%}"
         
        print(preColorSet + raw.format(
            num=project.id,
            name=project.name,
            complete=complete,
            progress="|" * round(30 * complete),
            
        ), postColorSet)
