from datetime import datetime, timedelta
import numpy as np
import cv2
from attendance.model import Attendance, Register
from user.Model import User


class QrReader:
    window_name = "Registro de asistencia"

    def __init__(self, id):
        try:
            self.attendance = Attendance.get(
                Attendance.turn == id, Attendance.date == datetime.now().date()
            )
        except Exception as e:
            self.attendance = Attendance.create(turn=id, date=datetime.now().date())
            self.bulk_registers()

        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

    def bulk_registers(self):
        users = User.select().where(User.turn == self.attendance.turn)
        registers = []
        for user in users:
            registers.append(
                Register(
                    user=user.id,
                    attendance=self.attendance.id,
                    status="Inasistencia",
                )
            )

        Register.bulk_create(registers)

    def read(self):
        capture = cv2.VideoCapture(0)

        while capture.isOpened():
            try:
                ret, img = capture.read()
                if not ret:
                    print("No se pudo abrir la camara")
                    break
                qrDetector = cv2.QRCodeDetector()
                data, bbox, _ = qrDetector.detectAndDecode(img)
                if bbox is not None:
                    if data:
                        points = np.array(bbox[0], dtype=np.int32).reshape((-1, 1, 2))
                        resp = self.assists_process(data)
                        if resp == 0:
                            cv2.polylines(img, [points], True, (0, 0, 255), 4)
                            cv2.putText(
                                img,
                                "Usuario no encontrado",
                                (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 0, 255),
                                2,
                            )

                        elif resp == 1:
                            cv2.polylines(img, [points], True, (0, 255, 0), 4)
                            cv2.putText(
                                img,
                                "Asistencia registrada",
                                (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 255, 0),
                                2,
                            )

                        elif resp == 2:
                            cv2.polylines(img, [points], True, (0, 255, 0), 4)
                            cv2.putText(
                                img,
                                "Asistencia registrada",
                                (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 255, 0),
                                2,
                            )

                        else:
                            cv2.polylines(img, [points], True, (0, 0, 255), 4)
                            cv2.putText(
                                img,
                                "Error al registrar",
                                (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                (0, 0, 255),
                                2,
                            )

                cv2.imshow(self.window_name, img)
                if cv2.waitKey(1) == ord("q"):
                    self.__del__()
                    break
                if cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE) < 1:
                    self.__del__()
                    break
            except Exception as e:
                print(e)

    def assists_process(self, dni):
        """
        returns
        0 if user not found
        1 if attendance already registered
        2 if attendance registered
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
            self.attendance.turn.time.hour,
            self.attendance.turn.time.minute,
            self.attendance.turn.time.second,
        ) + timedelta(minutes=self.attendance.turn.tolerance)

        try:

            register = Register.get(
                Register.user == user.id,
                Register.attendance == self.attendance.id,
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
                attendance=self.attendance.id,
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
