
from models import project_model, task_model


def create_tables():
    project_model.Project.create_table(True)
    task_model.Task.create_table(True)
