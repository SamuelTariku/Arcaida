from peewee import *
from utils.config import database


class Project(Model):
    name = CharField()
    started = BooleanField(default=False)

    class Meta:
        database = database
