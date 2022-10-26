from datetime import datetime
import sys
from UI.mainWindow import MainWindow
from attendance.model import Attendance, Register, Turn
from attendance.report import AttendanceReport
from user.Model import User
from PyQt5 import QtWidgets


def initDB():
    User.create_table()
    Attendance.create_table()
    Register.create_table()
    Turn.create_table()


def main():
    initDB()
    app = QtWidgets.QApplication(sys.argv)
    mi_app = MainWindow()
    mi_app.show()
    sys.exit(app.exec_())


if __name__ == "__main__":

    main()
    # AttendanceReport.generate(None, datetime(2022, 8, 1), datetime.now(), 1)
