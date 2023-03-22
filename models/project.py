from peewee import *
from models.base import PMS


class Project(PMS):
    name = CharField()
    started = BooleanField()


