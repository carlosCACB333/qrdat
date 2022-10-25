import peewee
from assistance.model_turn import Turn
from settings import DB, USER_TYPES


class User(peewee.Model):
    firstname = peewee.CharField(null=False)
    lastname = peewee.CharField(null=False)
    email = peewee.CharField(unique=True, null=True)
    dni = peewee.CharField(unique=True, null=False)
    phone = peewee.CharField(max_length=10)
    address = peewee.CharField()
    turn = peewee.ForeignKeyField(Turn, backref="users", on_delete="RESTRICT")
    userType = peewee.CharField(
        null=False,
        default=USER_TYPES[0][1],
        choices=USER_TYPES,
    )

    class Meta:
        database = DB
        db_table = "users"
