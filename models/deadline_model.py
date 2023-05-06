from peewee import *
from utils.config import database


class Deadline(Model):
    name = CharField()
    date = DateTimeField()

    class Meta:
        database = database
