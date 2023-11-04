from peewee import *
from utils.config import database


class Project(Model):
    name = CharField()
    active = BooleanField()
    class Meta:
        database = database
