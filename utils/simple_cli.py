from utils.log import Logger


class Command:
    def __init__(self, name, function, count=0) -> None:
        self.name = name
        self.count = count
        self.function = function


class CLI:
    def __init__(self) -> None:
        self.running = True
        self.prompt = "> "
        self.commands = {}

    def generateCommandDict(self, commands):
        commandDict = {}

        for command in commands:
            commandDict[command.name] = command

        exitCommand = Command("exit", self.close)
        helpCommand = Command("help", self.helpText)

        commandDict[exitCommand.name] = exitCommand
        commandDict[helpCommand.name] = helpCommand

        return commandDict

    def run(self):
        while self.running:
            argument = input(self.prompt)
            self.parse(argument)

    def parse(self, argument):
        argList = argument.split()

        if(len(argList) < 1):
            return

        command = self.commands.get(argList[0])

        if(command == None):
            Logger.error("No command with that name!")
            return

        if(command.count > (len(argList) - 1)):
            Logger.error("Not enough commands! Check documentation")
            print(argList)
            return

        if(command.count == 0):
            command.function()
        else:
            command.function(argList[1::])

    def close(self):
        self.running = False

    def helpText(self):
        print()
        print(" Command List \n", "_" * 30)
        for command in self.commands.keys():
            print(command)
        print()
