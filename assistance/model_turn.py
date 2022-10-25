from enum import unique
import peewee
from settings import DB


class Turn(peewee.Model):
    name = peewee.CharField(max_length=50, null=False, unique=True)
    time = peewee.TimeField(null=False)
    tolerance = peewee.IntegerField(null=False, default=5)

    def __str__(self):
        return self.name

    class Meta:
        database = DB
        db_table = "turns"
