
import models


def create_tables():
    models.project.Project.create_table(True)
    models.task.Task.create_table(True)
