from datetime import datetime, timedelta
import numpy as np
import cv2
from pyzbar.pyzbar import decode
from assistance.model import Assistance, Register
from user.Model import User


class QrReader:
    window_name = "Registro de asistencia"

    def __init__(self, id):
        try:
            self.assistance = Assistance.get(
                Assistance.turn == id, Assistance.date == datetime.now().date()
            )
        except Exception as e:
            self.assistance = Assistance.create(turn=id, date=datetime.now().date())
            self.bulk_registers()

        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        # onclose window

    def bulk_registers(self):
        users = User.select().where(User.turn == self.assistance.turn)
        registers = []
        for user in users:
            registers.append(
                Register(
                    user=user.id,
                    assistance=self.assistance.id,
                    status="Inasistencia",
                )
            )

        Register.bulk_create(registers)

    def read(self):

        while True:
            isShow, frame = self.cap.read()

            if isShow:
                for barcode in decode(frame):
                    email = barcode.data.decode("utf-8")
                    if email:

                        coord = np.array([barcode.polygon], np.int32).reshape(
                            (-1, 1, 2)
                        )
                        resp = self.assists_process(email)
                        if resp == 0:
                            cv2.polylines(frame, [coord], True, (0, 0, 255), 5)
                            cv2.putText(
                                frame,
                                "Usuario no encontrado",
                                (barcode.rect.left, barcode.rect.top - 5),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.9,
                                (0, 0, 255),
                                2,
                            )

                        elif resp == 1:
                            cv2.polylines(frame, [coord], True, (0, 255, 0), 5)
                            cv2.putText(
                                frame,
                                "Asistencia registrada",
                                (barcode.rect.left, barcode.rect.top - 5),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.9,
                                (0, 255, 0),
                                2,
                            )

                        elif resp == 2:
                            cv2.polylines(frame, [coord], True, (0, 255, 0), 5)
                            cv2.putText(
                                frame,
                                "Asistencia registrada",
                                (barcode.rect.left, barcode.rect.top - 5),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.9,
                                (0, 255, 0),
                                2,
                            )

                        else:
                            cv2.polylines(frame, [coord], True, (0, 0, 255), 5)
                            cv2.putText(
                                frame,
                                "Error al registrar la asistencia",
                                (barcode.rect.left, barcode.rect.top - 5),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.9,
                                (0, 0, 255),
                                2,
                            )

                cv2.imshow(self.window_name, frame)
                cv2.waitKey(1)
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                    self.__del__()
                    break

    def assists_process(self, dni):
        """
        returns
        0 if user not found
        1 if assistance already registered
        2 if assistance registered
        3 other error
        """

        user = User.get_or_none(User.dni == dni)
        if not user:
            return 0

        today = datetime.now()
        date_limit = datetime(
            today.year,
            today.month,
            today.day,
            self.assistance.turn.time.hour,
            self.assistance.turn.time.minute,
            self.assistance.turn.time.second,
        ) + timedelta(minutes=self.assistance.turn.tolerance)

        try:

            register = Register.get(
                Register.user == user.id,
                Register.assistance == self.assistance.id,
            )

            if register.time:
                return 1

            register.time = today.time()
            if today.time() <= date_limit.time():
                register.status = "Asistencia"
            else:
                register.status = "Tardanza"
            register.save()
            return 2

        except Register.DoesNotExist:
            register = Register(
                user=user.id,
                assistance=self.assistance.id,
                status="Asistencia"
                if today.time() <= date_limit.time()
                else "Tardanza",
                time=today.time(),
            )
            register.save()
            return 2
        except Exception as e:
            return 3

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()
