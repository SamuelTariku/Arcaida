from utils.log import Logger
import os


class Command:
    def __init__(self, name, function, count=0) -> None:
        self.name = name
        self.count = count
        self.function = function


class CLI:
    def __init__(self) -> None:
        self.running = True
        self.prompt = ""
        self.commands = {}

    def showScreen(self):
        raise NotImplemented

    def generateCommandDict(self, commands):
        commandDict = {}

        for command in commands:
            commandDict[command.name] = command

        commandDict["help"] = Command("help", self.helpText)
        commandDict["back"] = Command("back", self.back)
        commandDict["exit"] = Command("exit", self.close)

        return commandDict

    def run(self):
        exitValue = None

        while self.running:

            argument = input(self.prompt + "> ")
            exitValue = self.parse(argument)
        return exitValue

    def parse(self, argument):
        argList = argument.split()

        if len(argList) < 1:
            self.showScreen()
            return

        command = self.commands.get(argList[0])

        if command == None:
            self.showScreen()
            Logger.error("No command with that name!")
            return

        if command.count > (len(argList) - 1):
            self.showScreen()
            Logger.error("Not enough arguments! Check documentation")
            print(argList)
            return

        # All command functions need to take an argument
        exitValue = command.function(argList[1::])

        # if(command.count == 0):
        #     exitValue = command.function()
        # else:
        #     exitValue = command.function(argList[1::])

        return exitValue

    def close(self, args=[]):
        self.running = False
        return True

    def back(self, args=[]):

        self.running = False
        return False

    def helpText(self, args=[]):
        # TODO: Make this better
        Logger.clear()
        Logger.header()
        print()
        if self.prompt:
            print(self.prompt + " Command List \n", "_" * 30)
        else:
            print("Root Command List \n", "_" * 30)
        for command in self.commands.keys():
            print(command)
        input()
        self.showScreen()
