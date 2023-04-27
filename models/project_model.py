from peewee import *
from utils.config import database


class Project(Model):
    name = CharField()

    class Meta:
        database = database
