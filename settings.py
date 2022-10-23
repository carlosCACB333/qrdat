from peewee import SqliteDatabase

DB = SqliteDatabase("db.sqlite3")
USER_TYPES = [("Alumno", "Alumno"), ("Profesor", "Profesor"), ("Otro", "Otro")]
