
from models import project_model, task_model, deadline_model


def create_tables():
    project_model.Project.create_table(True)
    task_model.Task.create_table(True)
    deadline_model.Deadline.create_table(True)
