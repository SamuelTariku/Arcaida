from peewee import *
from utils.config import database
from models.project_model import Project
from enum import Enum


class Status(Enum):
    BACKLOG = 1
    IN_PROGRESS = 2
    TESTING = 3
    DONE = 4


class Task(Model):
    name = CharField()
    status = IntegerField(default=1)
    project = ForeignKeyField(Project, backref="tasks")
    order = IntegerField(null=True)

    class Meta:
        database = database
        # indexes = (
        #     (('project', 'order'), True),
        # )
