from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from assistance.service import AssistanceService
from user.service import UserService


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("UI/mainWindow.ui", self)
        self.events()
        self.show()
        self.userService = UserService(self)
        self.assistanceService = AssistanceService(self)

    def events(self):
        self.btn_home.clicked.connect(
            lambda: self.stackedWidget.setCurrentWidget(self.page_home)
        )
        self.btn_assistance.clicked.connect(lambda: self.assistanceService.on_active())
        self.btn_user.clicked.connect(lambda: self.userService.on_active())
        self.btn_report_all.clicked.connect(
            lambda: self.assistanceService.on_report_all()
        )
        self.btn_user_save.clicked.connect(lambda: self.userService.save())

    def show_message(self, message, type="info"):
        if type == "info":
            self.statusbar.showMessage(message, 2000)
            self.statusbar.setStyleSheet("color: green")
        elif type == "error":
            self.statusbar.showMessage(message, 5000)
            self.statusbar.setStyleSheet("color: red")
