import datetime
from peewee import *
from utils.config import database


class Project(Model):
    name = CharField()
    active = BooleanField()
    created = DateTimeField(default=datetime.datetime.now)
    updated = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated = datetime.datetime.now()
        return super(Project, self).save(*args, **kwargs)
    
    class Meta:
        database = database
