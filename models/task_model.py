import datetime
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
    project = ForeignKeyField(Project, backref="tasks", on_delete="CASCADE")
    order = IntegerField(null=True)
    # deadline = ForeignKeyField(
    #     Deadline, null=True, backref="tasks", on_delete="CASCADE"
    # )
    startDate = DateTimeField(null=True)
    endDate = DateTimeField(null=True)
    created = DateTimeField(default=datetime.datetime.now)
    updated = DateTimeField(default=datetime.datetime.now)
    description = TextField(null=True)

    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        return super(Task, self).save(*args, **kwargs)

    class Meta:
        database = database
        # indexes = (
        #     (('project', 'order'), True),
        # )
