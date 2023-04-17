from art import tprint
from cli.root_cli import BaseCLI
from models import create_tables
from utils.config import database
from utils.log import Logger
from colorama import init, deinit, Fore, Style


init()


# Generate header text
print("-" * 50)

tprint("Arcadia", font="utopiab")

print("-" * 50)

# connect to the database
Logger.info("connecting to database...")
database.connect()
create_tables()
Logger.success("database connected!")

# setup cli
app = BaseCLI()
app.run()


deinit()
