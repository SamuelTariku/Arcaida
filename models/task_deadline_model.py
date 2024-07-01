from models.task_model import Task
from models.deadline_model import Deadline

from peewee import *
from utils.config import database


class TaskDeadline(Model):
    task = ForeignKeyField(
        Task, backref="deadlines", on_delete="CASCADE", on_update="CASCADE"
    )
    deadline = ForeignKeyField(
        Deadline, backref="tasks", on_delete="CASCADE", on_update="CASCADE"
    )

    class Meta:
        database = database
        indexes = ((("task", "deadline"), True),)
