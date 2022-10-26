from datetime import datetime
import peewee
from attendance.model_turn import Turn
from settings import DB
from user.Model import User


class Attendance(peewee.Model):
    date = peewee.DateField(null=False, default=datetime.now)
    turn = peewee.ForeignKeyField(Turn, backref="assistances", on_delete="RESTRICT")

    def __str__(self):
        return f"{self.date} - {self.turn}"

    class Meta:
        database = DB
        db_table = "attendance"
        indexes = ((("date", "turn"), True),)


class Register(peewee.Model):
    time = peewee.TimeField(null=True)
    user = peewee.ForeignKeyField(User, backref="registers", on_delete="RESTRICT")
    attendance = peewee.ForeignKeyField(
        Attendance, backref="registers", on_delete="RESTRICT"
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
        return f"{self.user} - {self.attendance} - {self.status}"

    class Meta:
        database = DB
        db_table = "registers"
