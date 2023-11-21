from art import tprint
from cli.root_cli import BaseCLI
from models import create_tables
from utils.config import database
from utils.log import Logger
from colorama import init, deinit, Fore, Style


init()


# Generate header text
print(Fore.LIGHTMAGENTA_EX, end="")
print("-" * 58)
tprint("Arcadia")
print("-" * 58)
print(Fore.RESET, end="")

# connect to the database
Logger.info("connecting to database...")
database.connect()
create_tables()
Logger.success("database connected!")

# setup cli
app = BaseCLI()
app.run()

Logger.info("closing arcadia...")
database.close()
Logger.success("Goodbye!")
deinit()
