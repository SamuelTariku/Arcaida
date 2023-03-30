from peewee import *
from models.base_model import PMS


class Habit(PMS):
    name = CharField()
    
