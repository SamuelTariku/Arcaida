from peewee import *
from utils.config import database


class Deadline(Model):
    name = CharField()
    date = DateField()

    class Meta:
        database = database
