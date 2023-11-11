from utils.log import Logger


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

        if(len(argList) < 1):
            return

        command = self.commands.get(argList[0])

        if(command == None):
            Logger.error("No command with that name!")
            return

        if(command.count > (len(argList) - 1)):
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
        print()
        print(" Command List \n", "_" * 30)
        for command in self.commands.keys():
            print(command)
        print()
