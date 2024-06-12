from peewee import *
from utils.config import database
from enum import Enum


class DeadlineStates(Enum):
    PENDING = 1
    COMPLETE = 2


class Deadline(Model):
    name = CharField()
    date = DateTimeField()
    state = IntegerField(default=1)

    class Meta:
        database = database
