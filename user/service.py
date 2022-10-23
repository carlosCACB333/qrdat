from assistance.model import Turn
from .Model import User
from PyQt5.QtWidgets import QTableWidgetItem


class UserService:
    def __init__(self, window):
        self.window = window

    def onActive(self):
        self.window.stackedWidget.setCurrentWidget(self.window.page_user)
        self.fillTable()
        self.fill_combobox_turns()

    def fill_combobox_turns(self):
        self.window.cmb_user_turns.clear()
        turns = Turn.select()
        for turn in turns:
            time = turn.time.strftime("%I:%M %p")
            self.window.cmb_user_turns.addItem(
                "{} - {}".format(turn.name, time), turn.id
            )

    def save(self):
        firstname = self.window.txt_user_firstname.text()
        lastname = self.window.txt_user_lastname.text()
        email = self.window.txt_user_email.text()
        dni = self.window.txt_user_dni.text()
        phone = self.window.txt_user_phone.text()
        address = self.window.txt_user_address.text()
        userType = self.window.cmb_user_type.currentText()
        turn = self.window.cmb_user_turns.currentData()
        if firstname and lastname and dni and turn:
            user = User(
                firstname=firstname,
                lastname=lastname,
                email=email if email != "" else None,
                dni=dni,
                phone=phone,
                address=address,
                userType=userType,
                turn=turn,
            )
            try:
                user.save()
                self.fillTable()
                self.window.show_message("Usuario guardado correctamente")
                self.window.txt_user_firstname.setText("")
                self.window.txt_user_lastname.setText("")
                self.window.txt_user_email.setText("")
                self.window.txt_user_dni.setText("")
                self.window.txt_user_phone.setText("")
                self.window.txt_user_address.setText("")
                self.window.cmb_user_type.setCurrentIndex(0)
            except Exception as e:
                self.window.show_message(str(e), "error")

        else:
            self.window.show_message("Llene todos los campos", "error")

    def fillTable(self):
        users = User.select()
        self.window.table_user.setRowCount(len(users))
        for i, user in enumerate(users):
            self.window.table_user.setItem(i, 0, QTableWidgetItem(user.firstname))
            self.window.table_user.setItem(i, 1, QTableWidgetItem(user.lastname))
            self.window.table_user.setItem(i, 2, QTableWidgetItem(user.dni))
            self.window.table_user.setItem(i, 3, QTableWidgetItem(user.email))
            self.window.table_user.setItem(i, 4, QTableWidgetItem(user.address))
            self.window.table_user.setItem(i, 5, QTableWidgetItem(user.phone))
            self.window.table_user.setItem(i, 6, QTableWidgetItem(user.userType))
            self.window.table_user.setItem(i, 7, QTableWidgetItem(user.turn.name))

        self.window.table_user.resizeColumnsToContents()
        self.window.table_user.resizeRowsToContents()

    findByEmail = staticmethod(lambda email: User.get(User.email == email))
