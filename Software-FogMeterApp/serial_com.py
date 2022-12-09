import serial
import serial.tools.list_ports
import time


class SerialCom:
    """Administra todo respecto a la comunicación en serie con pyserial."""

    def __init__(self):
        """Inicializar parámetros de conección."""
        self.arduino_ser = serial.Serial()
        self.actual_baudrate = 38400
        self.actual_port = None
        self.actual_val = ""
        self.update_ports()

    def update_ports(self):
        """Actualizar los puertos en una lista."""
        self.ports = serial.tools.list_ports.comports()
        self.port_list = []
        for one_port in self.ports:
            self.port_list.append(str(one_port))

    def _update_serial_params(self):
        """Asignar los parámetros de conección."""
        self.arduino_ser.baudrate = self.actual_baudrate
        self.arduino_ser.port = self.actual_port

    def open_and_write(self, command):
        """Empezar la comunicación y mandar un comando."""
        self._update_serial_params()
        self.arduino_ser.open()
        self.arduino_ser.write(bytes(command, 'utf-8'))

    def receive_data(self, data_list=[], save_data=True):
        """Recibir una línea de datos y almacenarlo opcionalmente en una lista."""
        if self.arduino_ser.in_waiting:
            bytes_data = self.arduino_ser.readline()
            str_data = bytes_data.decode('utf').strip()
            if str_data.lower() == "done":
                return False
            else:
                if save_data:
                    data_list.append(float(str_data))
                self.actual_val = str_data
                return True
        else:
            time.sleep(0.01)
            return True
