from datetime import datetime, timedelta
from user.Model import User
from .model import Assistance, Register, Turn
from qrReader import QrReader
from PyQt5.QtWidgets import QTableWidgetItem
from peewee import fn


class AssistanceService:
    def __init__(self, window):
        self.window = window
        self.window.btn_assistance_pass.clicked.connect(self.pass_assistance)
        self.window.btn_turn_save.clicked.connect(self.turn_save)
        self.window.btn_turns.clicked.connect(self.on_turns)
        self.window.btn_report_show.clicked.connect(self.fill_table_report)

        self.window.dt_report_start.setDate(
            (datetime.now() - timedelta(days=30)).date()
        )
        self.window.dt_report_end.setDate(datetime.now().date())
        self.get_user_report()

    def on_active(self):
        self.window.stackedWidget.setCurrentWidget(self.window.page_assistance)
        self.fill_cmb_assistance_turns()

    def on_report_all(self):
        self.window.stackedWidget.setCurrentWidget(self.window.page_report_all)

    def on_turns(self):
        self.window.stackedWidget.setCurrentWidget(self.window.page_turns)
        self.fill_table_turns()

    def fill_cmb_assistance_turns(self):
        self.window.cmb_assistance_turns.clear()
        turns = Turn.select()
        for turn in turns:
            time = turn.time.strftime("%I:%M %p")
            self.window.cmb_assistance_turns.addItem(
                "{} - {}".format(turn.name, time), turn.id
            )

    def turn_save(self):
        name = self.window.txt_turn_name.text()
        time = self.window.tm_turn_time.time().toString()
        tolerance = self.window.sp_turn_tolerance.value()
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
        for i, turn in enumerate(turns):
            self.window.tbl_turns.setItem(i, 0, QTableWidgetItem(turn.name))
            self.window.tbl_turns.setItem(i, 1, QTableWidgetItem(str(turn.time)))
            self.window.tbl_turns.setItem(i, 2, QTableWidgetItem(str(turn.tolerance)))

    def get_assistance_today(self):
        assistance = Assistance.select().where(Assistance.date == datetime.now().date())
        return assistance

    def insert_registers(self, assistance):
        users = User.select()
        registers = []
        for user in users:
            registers.append(
                Register(user=user, assistance=assistance, status="Inasistencia")
            )
        Register.bulk_create(registers)

    def pass_assistance(self):
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
        (dni, firstname, lastname, count_assistance,userType, count_tardy, count_absence)
        """
        dt_report_start = self.window.dt_report_start.date().toPyDate()
        dt_report_end = self.window.dt_report_end.date().toPyDate()
        users = (
            User.select(
                User.dni,
                User.firstname,
                User.lastname,
                User.userType,
                fn.SUM(Register.status == "Asistencia").alias("count_assistance"),
                fn.SUM(Register.status == "Tardanza").alias("count_tardy"),
                fn.SUM(Register.status == "Inasistencia").alias("count_absence"),
            )
            .join(Register)
            .join(Assistance)
            .where(
                (Assistance.date >= dt_report_start)
                & (Assistance.date <= dt_report_end)
            )
            .group_by(User.dni)
        )

        return users

    def fill_table_report(self):
        users = self.get_user_report()
        self.window.tbl_report.setRowCount(len(users))
        for i, user in enumerate(users):
            self.window.tbl_report.setItem(i, 0, QTableWidgetItem(user.dni))
            self.window.tbl_report.setItem(i, 1, QTableWidgetItem(user.firstname))
            self.window.tbl_report.setItem(i, 2, QTableWidgetItem(user.lastname))
            self.window.tbl_report.setItem(i, 3, QTableWidgetItem(user.userType))
            self.window.tbl_report.setItem(
                i, 4, QTableWidgetItem(str(user.count_assistance))
            )
            self.window.tbl_report.setItem(
                i, 5, QTableWidgetItem(str(user.count_tardy))
            )
            self.window.tbl_report.setItem(
                i, 6, QTableWidgetItem(str(user.count_absence))
            )
