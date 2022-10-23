import sys
from UI.mainWindow import MainWindow
from assistance.model import Assistance, Register, Turn
from user.Model import User
from PyQt5 import QtWidgets


def initDB():
    User.create_table()
    Assistance.create_table()
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
