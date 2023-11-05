from peewee import *
from utils.config import database
from models.project_model import Project
from models.deadline_model import Deadline
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
    deadline = ForeignKeyField(Deadline, null=True, backref="tasks")
    startDate = DateTimeField(null=True)
    endDate = DateTimeField(null=True)
    
    class Meta:
        database = database
        # indexes = (
        #     (('project', 'order'), True),
        # )
