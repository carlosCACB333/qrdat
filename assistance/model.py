from datetime import datetime
import peewee
from assistance.model_turn import Turn
from settings import DB
from user.Model import User


class Assistance(peewee.Model):
    date = peewee.DateField(null=False, default=datetime.now)
    turn = peewee.ForeignKeyField(Turn, backref="assistances", on_delete="RESTRICT")

    def __str__(self):
        return self.name

    class Meta:
        database = DB
        db_table = "assists"
        indexes = ((("date", "turn"), True),)


class Register(peewee.Model):
    time = peewee.TimeField(null=True)
    user = peewee.ForeignKeyField(User, backref="registers", on_delete="RESTRICT")
    assistance = peewee.ForeignKeyField(
        Assistance, backref="registers", on_delete="RESTRICT"
    )
    status = peewee.CharField(
        null=False,
        choices=[
            ("Asistencia", "Asistencia"),
            ("Inasistencia", "Inasistencia"),
            ("Tardanza", "Tardanza"),
        ],
    )

    def __str__(self):
        return self.name

    class Meta:
        database = DB
        db_table = "registers"
