from functools import partial
from peewee import *
import datetime
import os

db = SqliteDatabase('data/uo-words.db')

class BaseModel(Model):
    class Meta:
        database = db