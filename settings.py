from peewee import SqliteDatabase

DB = SqliteDatabase("db.sqlite3", pragmas={"foreign_keys": 1})
USER_TYPES = [("Alumno", "Alumno"), ("Profesor", "Profesor"), ("Otro", "Otro")]
MENU_STYLE = """
            QMenu {
                background-color: #2D2D2D;
                color: #fff;
            }
            QMenu::item:selected {
                background-color: #3D3D3D;
            }
            """
