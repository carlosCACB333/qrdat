from assistance.model import Turn
from settings import MENU_STYLE, USER_TYPES
from .Model import User
from PyQt5.QtWidgets import QTableWidgetItem, QMenu
from PyQt5.QtCore import Qt


class UserService:
    def __init__(self, window):
        self.window = window
        self.create_Context_Menu()

    def on_active(self):
        self.window.stackedWidget.setCurrentWidget(self.window.page_user)
        self.fill_table()
        self.fill_combobox_turns()
        self.fill_combobox_usertypes()

    def fill_combobox_turns(self):
        self.window.cmb_user_turns.clear()
        turns = Turn.select()
        for turn in turns:
            time = turn.time.strftime("%I:%M %p")
            self.window.cmb_user_turns.addItem(
                "{} - {}".format(turn.name, time), turn.id
            )

    def fill_combobox_usertypes(self):
        self.window.cmb_user_type.clear()
        for userType in USER_TYPES:
            self.window.cmb_user_type.addItem(userType[0], userType[1])

    def _get_fields_user(self):
        firstname = self.window.txt_user_firstname.text()
        lastname = self.window.txt_user_lastname.text()
        email = self.window.txt_user_email.text()
        dni = self.window.txt_user_dni.text()
        phone = self.window.txt_user_phone.text()
        address = self.window.txt_user_address.text()
        userType = self.window.cmb_user_type.currentText()
        turn = self.window.cmb_user_turns.currentData()
        return firstname, lastname, email, dni, phone, address, userType, turn

    def _set_fields_user(self, user):
        self.window.txt_user_firstname.setText(user.firstname)
        self.window.txt_user_lastname.setText(user.lastname)
        self.window.txt_user_email.setText(user.email)
        self.window.txt_user_dni.setText(user.dni)
        self.window.txt_user_phone.setText(user.phone)
        self.window.txt_user_address.setText(user.address)
        self.window.cmb_user_type.setCurrentText(user.userType)
        self.window.cmb_user_turns.setCurrentText(user.turn.name)

    def _reset_forms(self):
        self.window.txt_user_firstname.setText("")
        self.window.txt_user_lastname.setText("")
        self.window.txt_user_email.setText("")
        self.window.txt_user_dni.setText("")
        self.window.txt_user_phone.setText("")
        self.window.txt_user_address.setText("")
        self.window.cmb_user_type.setCurrentIndex(0)
        self.window.cmb_user_turns.setCurrentIndex(0)

    def save(self):
        (
            firstname,
            lastname,
            email,
            dni,
            phone,
            address,
            userType,
            turn,
        ) = self._get_fields_user()
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
                self.fill_table()
                self._reset_forms()
                self.window.show_message("Usuario guardado correctamente")
            except Exception as e:
                self.window.show_message(str(e), "error")

        else:
            self.window.show_message("Llene todos los campos", "error")

    def fill_table(self):
        users = User.select()
        self.window.table_user.setRowCount(len(users))
        self.window.table_user.setColumnHidden(0, True)
        for index, user in enumerate(users):
            self.window.table_user.setItem(index, 0, QTableWidgetItem(str(user.id)))
            self.window.table_user.setItem(index, 1, QTableWidgetItem(user.firstname))
            self.window.table_user.setItem(index, 2, QTableWidgetItem(user.lastname))
            self.window.table_user.setItem(index, 3, QTableWidgetItem(user.dni))
            self.window.table_user.setItem(index, 4, QTableWidgetItem(user.email))
            self.window.table_user.setItem(index, 5, QTableWidgetItem(user.address))
            self.window.table_user.setItem(index, 6, QTableWidgetItem(user.phone))
            self.window.table_user.setItem(index, 7, QTableWidgetItem(user.userType))
            self.window.table_user.setItem(index, 8, QTableWidgetItem(user.turn.name))

    findByEmail = staticmethod(lambda email: User.get(User.email == email))

    def create_Context_Menu(self):
        self.window.table_user.setContextMenuPolicy(Qt.CustomContextMenu)
        self.window.table_user.customContextMenuRequested.connect(
            self.show_context_menu
        )

    def show_context_menu(self, position):
        menu = QMenu()
        # style
        menu.setStyleSheet(MENU_STYLE)

        item = self.window.table_user.itemAt(position)
        if item:
            menu.addAction("Eliminar", self.delete)
            menu.addAction("Editar", self.edit)
            menu.exec_(self.window.table_user.viewport().mapToGlobal(position))

    def delete(self):
        row = self.window.table_user.currentRow()
        id = self.window.table_user.item(row, 0).text()
        try:
            User.delete_by_id(id)
            self.fill_table()
            self.window.show_message("Usuario eliminado correctamente")
        except Exception as e:
            self.window.show_message(str(e), "error")

    def edit(self):
        row = self.window.table_user.currentRow()
        id = self.window.table_user.item(row, 0).text()
        user = User.get(User.id == id)
        self._set_fields_user(user)
        self.window.btn_user_save.clicked.disconnect()
        self.window.btn_user_save.clicked.connect(self.update)
        self.window.btn_user_save.setText("Actualizar")

    def update(self):
        row = self.window.table_user.currentRow()
        id = self.window.table_user.item(row, 0).text()
        try:
            user = User.get(User.id == id)
            (
                user.firstname,
                user.lastname,
                user.email,
                user.dni,
                user.phone,
                user.address,
                user.userType,
                user.turn,
            ) = self._get_fields_user()
            user.save()
            self.fill_table()
            self._reset_forms()
            self.window.show_message("Usuario actualizado correctamente")
            self.window.btn_user_save.clicked.disconnect()
            self.window.btn_user_save.clicked.connect(self.save)
            self.window.btn_user_save.setText("Guardar")
        except Exception as e:
            self.window.show_message(str(e), "error")
