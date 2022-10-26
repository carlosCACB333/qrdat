from datetime import datetime, timedelta

from black import Report
from attendance.report import AttendanceReport
from settings import MENU_STYLE
from user.Model import User
from .model import Attendance, Register, Turn
from qrReader import QrReader
from PyQt5.QtWidgets import QTableWidgetItem, QMenu
from PyQt5.QtCore import Qt
from peewee import fn


class AttendanceService:
    def __init__(self, window):
        self.window = window
        self.window.btn_assistance_pass.clicked.connect(self.pass_attendance)
        self.window.btn_turn_save.clicked.connect(self.save_turn)
        self.window.btn_turns.clicked.connect(self.on_turns)
        self.window.btn_report_show.clicked.connect(self.fill_table_report)
        self.window.btn_current_registers.clicked.connect(
            self.fill_table_current_registers
        )
        self.window.tbl_report.setColumnHidden(0, True)
        self.create_context_menu_turns()
        self.create_context_menu_report()
        self.window.dt_report_start.setDate(
            (datetime.now() - timedelta(days=30)).date()
        )
        self.window.btn_report_all.clicked.connect(lambda: self.on_report_all())
        self.window.btn_report_excel.clicked.connect(lambda: self.generate_excel())
        self.window.dt_report_end.setDate(datetime.now().date())

    def on_active(self):
        self.window.stackedWidget.setCurrentWidget(self.window.page_assistance)
        self.fill_cmb_turns(self.window.cmb_assistance_turns)

    def on_report_all(self):
        self.window.stackedWidget.setCurrentWidget(self.window.page_report_all)
        self.fill_cmb_turns(self.window.cmb_report_turns)

    def on_turns(self):
        self.window.stackedWidget.setCurrentWidget(self.window.page_turns)
        self.fill_table_turns()

    def fill_cmb_turns(self, cbm):
        cbm.clear()
        turns = Turn.select()
        for turn in turns:
            time = turn.time.strftime("%I:%M %p")
            cbm.addItem("{} - {}".format(turn.name, time), turn.id)

    def _get_turn_fields(self):
        name = self.window.txt_turn_name.text()
        time = self.window.tm_turn_time.time().toString()
        tolerance = self.window.sp_turn_tolerance.value()
        return name, time, tolerance

    def _set_turn_fields(self, turn):
        self.window.txt_turn_name.setText(turn.name)
        self.window.tm_turn_time.setTime(turn.time)
        self.window.sp_turn_tolerance.setValue(turn.tolerance)

    def save_turn(self):
        name, time, tolerance = self._get_turn_fields()
        if name and time:
            try:
                Turn.create(name=name, time=time, tolerance=tolerance)
                self.window.show_message("Turno creado correctamente", "info")
                self.fill_table_turns()
                self.window.txt_turn_name.setText("")
            except Exception as e:
                self.window.show_message(str(e), "error")
        else:
            self.window.show_message("Llene todos los campos", "error")

    def fill_table_turns(self):
        turns = Turn.select()
        self.window.tbl_turns.setRowCount(len(turns))
        self.window.tbl_turns.setColumnHidden(0, True)
        for i, turn in enumerate(turns):
            self.window.tbl_turns.setItem(i, 0, QTableWidgetItem(str(turn.id)))
            self.window.tbl_turns.setItem(i, 1, QTableWidgetItem(turn.name))
            self.window.tbl_turns.setItem(i, 2, QTableWidgetItem(str(turn.time)))
            self.window.tbl_turns.setItem(i, 3, QTableWidgetItem(str(turn.tolerance)))

    def get_attendance_today(self):
        attendance = Attendance.select().where(Attendance.date == datetime.now().date())
        return attendance

    def insert_registers(self, attendance):
        users = User.select()
        registers = []
        for user in users:
            registers.append(
                Register(user=user, attendance=attendance, status="Inasistencia")
            )
        Register.bulk_create(registers)

    def pass_attendance(self):
        id_turn = self.window.cmb_assistance_turns.currentData()
        if id_turn:
            try:
                QrReader(id_turn).read()
            except Exception as e:
                self.window.show_message(str(e), "error")
        else:
            self.window.show_message("Seleccione una asistencia", "error")

    def get_user_report(self):
        """
        returns a list of tuples with the following structure:
        (id,dni, firstname, lastname, userType, count_attendance,count_tardy, count_absence)
        """
        dt_report_start = self.window.dt_report_start.date().toPyDate()
        dt_report_end = self.window.dt_report_end.date().toPyDate()
        id_turn = self.window.cmb_report_turns.currentData()
        if not id_turn:
            self.window.show_message("Seleccione un turno", "error")
            return

        users = (
            User.select(
                User.id,
                User.dni,
                User.firstname,
                User.lastname,
                User.userType,
                fn.SUM(Register.status == "Asistencia").alias("count_attendance"),
                fn.SUM(Register.status == "Tardanza").alias("count_tardy"),
                fn.SUM(Register.status == "Inasistencia").alias("count_absence"),
            )
            .join(Register)
            .join(Attendance)
            .where(
                (Attendance.date >= dt_report_start)
                & (Attendance.date <= dt_report_end)
                & (User.turn == id_turn)
            )
            .group_by(User.dni)
            .order_by(fn.Lower(User.lastname))
        )

        return users

    def get_current_registers(self, turn_id):
        registers = (
            Register.select()
            .join(Attendance)
            .join(User, on=(Register.user == User.id))
            .where(
                (Attendance.date == datetime.now().date())
                & (Attendance.turn == turn_id)
            )
        )

        return registers

    def get_register_by_uid(self, uid):
        register = Register.select().where(Register.user == uid)
        return register

    def fill_table_report(self):
        users = self.get_user_report()
        self.window.tbl_report.setRowCount(len(users))

        for i, user in enumerate(users):
            self.window.tbl_report.setItem(i, 0, QTableWidgetItem(str(user.id)))
            self.window.tbl_report.setItem(i, 1, QTableWidgetItem(user.dni))
            self.window.tbl_report.setItem(i, 2, QTableWidgetItem(user.lastname))
            self.window.tbl_report.setItem(i, 3, QTableWidgetItem(user.firstname))
            self.window.tbl_report.setItem(i, 4, QTableWidgetItem(user.userType))
            self.window.tbl_report.setItem(
                i, 5, QTableWidgetItem(str(user.count_attendance))
            )
            self.window.tbl_report.setItem(
                i, 6, QTableWidgetItem(str(user.count_tardy))
            )
            self.window.tbl_report.setItem(
                i, 7, QTableWidgetItem(str(user.count_absence))
            )

    def create_context_menu_turns(self):
        self.window.tbl_turns.setContextMenuPolicy(Qt.CustomContextMenu)
        self.window.tbl_turns.customContextMenuRequested.connect(
            self.show_context_menu_turns
        )

    def show_context_menu_turns(self, pos):
        menu = QMenu()
        menu.setStyleSheet(MENU_STYLE)
        item = self.window.tbl_turns.itemAt(pos)
        if item:
            menu.addAction("Eliminar", self.delete_turn)
            menu.addAction("Editar", self.edit_turn)
            menu.exec_(self.window.tbl_turns.mapToGlobal(pos))

    def delete_turn(self):
        row = self.window.tbl_turns.currentRow()
        id = self.window.tbl_turns.item(row, 0).text()
        try:
            Turn.delete_by_id(id)
            self.window.show_message("Turno eliminado correctamente", "info")
            self.fill_table_turns()
        except Exception as e:
            self.window.show_message(str(e), "error")

    def edit_turn(self):
        row = self.window.tbl_turns.currentRow()
        id = self.window.tbl_turns.item(row, 0).text()
        turn = Turn.get_by_id(id)
        self._set_turn_fields(turn)
        self.window.btn_turn_save.clicked.disconnect()
        self.window.btn_turn_save.clicked.connect(self.update_turn)
        self.window.btn_turn_save.setText("Actualizar")

    def update_turn(self):
        row = self.window.tbl_turns.currentRow()
        id = self.window.tbl_turns.item(row, 0).text()

        try:
            turn = Turn.get_by_id(id)
            name, time, tolerance = self._get_turn_fields()
            turn.name = name
            turn.time = time
            turn.tolerance = tolerance
            turn.save()
            self.window.show_message("Turno actualizado correctamente", "info")
            self.fill_table_turns()
            self.window.txt_turn_name.setText("")
            self.window.btn_turn_save.clicked.disconnect()
            self.window.btn_turn_save.clicked.connect(self.save_turn)
            self.window.btn_turn_save.setText("Guardar")
        except Exception as e:
            self.window.show_message(str(e), "error")

    def create_context_menu_report(self):
        self.window.tbl_report.setContextMenuPolicy(Qt.CustomContextMenu)
        self.window.tbl_report.customContextMenuRequested.connect(
            self.show_context_menu_report
        )

    def show_context_menu_report(self, pos):
        menu = QMenu()
        menu.setStyleSheet(MENU_STYLE)
        item = self.window.tbl_report.itemAt(pos)
        uid = self.window.tbl_report.item(item.row(), 0).text()
        if item:
            menu.addAction("Ver detalle", lambda: self.on_show_report_detail(uid))
            menu.exec_(self.window.tbl_report.mapToGlobal(pos))

    def on_show_report_detail(self, uid):
        self.window.stackedWidget.setCurrentWidget(self.window.page_report_detail)
        self.fill_table_report_detail(uid)

    def fill_table_report_detail(self, uid):
        registers = self.get_register_by_uid(uid)
        self.window.tbl_report_detail.setColumnHidden(0, True)
        self.window.tbl_report_detail.setRowCount(len(registers))
        user = registers[0].user
        self.window.lbl_report_detail.setText(
            f"Registro  de {user.firstname} {user.lastname}"
        )
        for i, register in enumerate(registers):
            self.window.tbl_report_detail.setItem(
                i, 0, QTableWidgetItem(str(register.id))
            )
            self.window.tbl_report_detail.setItem(
                i, 1, QTableWidgetItem(register.attendance.date.strftime("%d/%m/%y"))
            )
            self.window.tbl_report_detail.setItem(
                i,
                2,
                QTableWidgetItem(
                    register.time.strftime("%I:%S:%M %p") if register.time else "--"
                ),
            )
            self.window.tbl_report_detail.setItem(
                i, 3, QTableWidgetItem(register.status)
            )

    def fill_table_current_registers(self):
        id_turn = self.window.cmb_assistance_turns.currentData()
        if not id_turn:
            self.window.show_message("Seleccione una asistencia", "error")
            return

        registers = self.get_current_registers(id_turn)
        self.window.tbl_current_registers.setColumnHidden(0, True)
        self.window.tbl_current_registers.setRowCount(len(registers))
        for i, register in enumerate(registers):
            self.window.tbl_current_registers.setItem(
                i, 0, QTableWidgetItem(str(register.id))
            )
            self.window.tbl_current_registers.setItem(
                i, 1, QTableWidgetItem(register.user.firstname)
            )
            self.window.tbl_current_registers.setItem(
                i, 2, QTableWidgetItem(register.user.lastname)
            )
            self.window.tbl_current_registers.setItem(
                i, 3, QTableWidgetItem(register.user.dni)
            )
            self.window.tbl_current_registers.setItem(
                i, 4, QTableWidgetItem(register.user.userType)
            )
            self.window.tbl_current_registers.setItem(
                i, 5, QTableWidgetItem(register.attendance.turn.name)
            )
            self.window.tbl_current_registers.setItem(
                i,
                6,
                QTableWidgetItem(
                    register.time.strftime("%I:%S:%M %p") if register.time else "--"
                ),
            )
            self.window.tbl_current_registers.setItem(
                i, 7, QTableWidgetItem(register.status)
            )

    def generate_excel(self):
        dt_start = self.window.dt_report_start.date().toPyDate()
        dt_end = self.window.dt_report_end.date().toPyDate()
        id_turn = self.window.cmb_report_turns.currentData()

        if not id_turn:
            self.window.show_message("Seleccione una asistencia", "error")
            return
        AttendanceReport.generate(self.window, dt_start, dt_end, id_turn)
