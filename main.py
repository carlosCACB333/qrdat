import sys
from attendance.model import Attendance, Register, Turn
from attendance.service import AttendanceService
from user.Model import User
from PyQt5.QtWidgets import QApplication, QMainWindow
from UI.main_window import Ui_MainWindow
from user.service import UserService


class MainWindows(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self._initDB()
        self.window = Ui_MainWindow()
        self.window.setupUi(self)
        self.show()
        self.events()
        self.window.show_message = self.show_message
        self.userService = UserService(self.window)
        self.assistanceService = AttendanceService(self.window)

    def _initDB(self):
        User.create_table()
        Attendance.create_table()
        Register.create_table()
        Turn.create_table()

    def events(self):
        self.window.btn_home.clicked.connect(
            lambda: self.window.stackedWidget.setCurrentWidget(self.window.page_home)
        )
        self.window.btn_assistance.clicked.connect(
            lambda: self.assistanceService.on_active()
        )
        self.window.btn_user.clicked.connect(lambda: self.userService.on_active())
        self.window.btn_user_save.clicked.connect(lambda: self.userService.save())

    def show_message(self, message, type="info"):
        if type == "info":
            self.window.statusbar.showMessage(message, 2000)
            self.window.statusbar.setStyleSheet("color: green")
        elif type == "error":
            self.window.statusbar.showMessage(message, 5000)
            self.window.statusbar.setStyleSheet("color: red")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindows()
    sys.exit(app.exec_())
