
from models.project import Project

def create_tables():
    Project.create_table(True)
