from peewee import *
from utils.config import database


class PMS(Model):
    class Meta:
        database = database
