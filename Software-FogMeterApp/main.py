from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.list import OneLineListItem
from kivy.clock import Clock
from functools import partial
# from kivymd.uix.picker import MDDatePicker
from kivy_garden.graph import Graph, MeshLinePlot
import numpy as np
import json
from datetime import datetime
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBodyTouch
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.card import MDCard
from kivymd.uix.list import TwoLineIconListItem
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDFillRoundFlatButton
from kivy.utils import platform
import database as db
from collections.abc import Iterable
from datetime import date
from datetime import datetime
from serial_com import SerialCom
import scipy.fft

"""
if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE,
                        Permission.WRITE_EXTERNAL_STORAGE])
"""

# Initialize db instance


class WindowManager(ScreenManager):
    """Window manager for changing screens"""
    pass

class TestDialog(MDDialog):
    """Administra métodos respecto al diálogo de 'test de lectura de datos'."""

    def on_pre_dismiss(self):
        """Procedimientos a realizar antes de cerrar el diálogo."""
        self.app = MDApp.get_running_app()
        try:
            self.screen.reception_event.cancel()  # Terminar bucle de lectura.
        except AttributeError:
            pass
        #self.screen.data_list = [20, 16, 14]
        # self.screen.save_data(self.screen.data_list) # Datos de prueba para probar el almacenamiento
        self.app.ser_com.arduino_ser.close()  # Cerrar la instancia de serial.
        return super().on_pre_dismiss()

class ConnectItemSelect(TwoLineIconListItem):
    """Administra métodos respecto al diálogo de selección de puerto de comunicación."""

    def setter(self, instance_check):
        """Establece el ícono correcto y almacena el puerto actual."""
        self.set_icon(instance_check)
        self.set_actual_port()

    def set_icon(self, instance_check):
        """Marca la casilla de check con su selección."""
        instance_check.active = True
        check_list = instance_check.get_widgets(instance_check.group)
        for check in check_list:
            if check != instance_check:
                check.active = False

    def set_actual_port(self):
        """Establece el puerto actual como el seleccionado."""
        self.app = MDApp.get_running_app()
        self.app.ser_com.actual_port = self.text

        if self.app.ser_com.actual_port:
            self.screen = self.app.root.get_screen("monitor_window")
            self.screen.ids.start_test_button.disabled = False
            # Habilita el botón para iniciar tests.


class LoginWindow(Screen):

    def on_enter(self, *args):
        self.manager.transition.direction = "left"
        return super().on_enter(*args)

    def login(self):
        dni = self.ids.user_login_dni.text
        pwd = self.ids.user_login_password.text

        info = list(db.patient_info(dni)) if isinstance(
            db.patient_info(dni), Iterable) else None
        if info != None:
            if pwd == info[1]:
                self.app = MDApp.get_running_app()
                self.app.current_user_data = list(info)
                self.app.root.current = "start_window"
            else:
                pass
                # print("Contraseña incorrecta")
        else:
            pass
            # print("El DNI no está registrado")


class RegisterWindow(Screen):
    def register(self):
        self.user_data = [
            self.ids.user_dni.text,
            self.ids.user_password.text,
            self.ids.user_name.text,
            "",
            "",
            "",
            "",
            "{}",
            "{}"
        ]

        if self.confirm_register():
            db.new_patient(*self.user_data)
            self.app = MDApp.get_running_app()
            self.app.current_user_data = self.user_data
            self.app.root.current = "personal_window"
        else:
            pass

    def confirm_register(self):
        return not (isinstance(db.patient_info(self.ids.user_dni.text), Iterable))


class PersonalWindow(Screen):
    user_sex = "F"

    def add_personal_data(self):
        self.app = MDApp.get_running_app()
        self.new_user_data = [
            "",
            "",
            "",
            self.ids.user_mail.text,
            self.ids.user_age.text,
            self.user_sex,
            self.ids.user_mail.text,
            "",
            ""
        ]

        for i in range(len(self.new_user_data)):
            if self.new_user_data[i] != "":
                self.app.current_user_data[i] = self.new_user_data[i]

        db.edit_patient(*self.app.current_user_data)
        print(self.app.current_user_data)
        self.app.root.current = "start_window"

    def on_checkbox_active(self, checkbox, value, sex):
        if value:
            self.user_sex = sex


class StartWindow(Screen):
    def on_enter(self, *args):
        self.manager.transition.direction = "left"
        return super().on_enter(*args)


class ConnectionDialog(MDDialog):
    """Administra métodos respecto a el diálogo de conección de puertos."""

    def on_open(self):
        """Procedimientos a realizar al abrir el diálogo."""
        if not self.items:
            self.title = "No se encontraron puertos disponibles, verifique que el dispositivo esté encendido."
        else:
            self.title = "Seleccionar puerto de comunicación"
        return super().on_open()

class MonitoringWindow(Screen):
    con_dialog = None
    test_dialog = None

    def start_connection(self):
        """Buscar los puertos disponibles y mostrarlos en un diálogo."""

        self.app = MDApp.get_running_app()
        self.app.ser_com.update_ports()
        ports = self.app.ser_com.port_list

        # Datos de prueba (para uso de depuracion):

        self.items_list = []
        self.list_port_items(ports)

        if not self.con_dialog:
            self.con_dialog = ConnectionDialog(
                title="Seleccionar puerto de comunicación",
                radius=[20, 7, 20, 7],
                type="confirmation",
                items=self.items_list,
                buttons=[
                    MDFlatButton(
                        text="CANCELAR",
                        theme_text_color="Custom",
                        text_color=MDApp.get_running_app().theme_cls.primary_dark,
                    ),
                    MDFlatButton(
                        text="CONFIRMAR",
                        theme_text_color="Custom",
                        text_color=MDApp.get_running_app().theme_cls.primary_dark,
                    ),
                ]
            )

        self.con_dialog.open()

    def list_port_items(self, ports):
        """Incluir los puertos en una pantalla de selección."""
        for port in ports:
            text_pair = port.split(" ", 1)
            item = ConnectItemSelect(
                text=text_pair[0], secondary_text=text_pair[1])
            self.items_list.append(item)

    def start_test(self):
        """Mostrar un diálogo con los botones de selección de sensor para lectura."""
        self.data_list = []

        if not self.test_dialog:

            # Crear 3 botones.
            self.button_list = [MDFillRoundFlatButton(
                text=f"Aceleración",
                theme_text_color="Custom",
                disabled=False,
                md_bg_color=MDApp.get_running_app().theme_cls.primary_dark,
            ),MDFillRoundFlatButton(
                text=f"Velocidad angular",
                theme_text_color="Custom",
                disabled=False,
                md_bg_color=MDApp.get_running_app().theme_cls.primary_dark,
            )
            ]

            # Crear el diálogo.
            self.test_dialog = TestDialog(
                title="Seleccione de qué quiere realizar el test:",
                radius=[20, 7, 20, 7],
                buttons=self.button_list
            )

            # Asignar funciones a los botones.
            self.button_list[0].bind(on_release=partial(self.read_sensor, "a"))
            self.button_list[1].bind(on_release=partial(self.read_sensor, "b"))

        self.test_dialog.open()

    def enable_buttons_back(self):
        """Rehabilitar los botones de lectura."""
        for i in range(len(self.button_list)):
            self.button_list[i].disabled = False

    def read_sensor(self, command, instance):
        """Leer el sensor seleccionado."""
        self.current_sensor = ord(command) - 96
        for i in range(len(self.button_list)):
            self.button_list[i].disabled = True

        self.app = MDApp.get_running_app()
        #print("Connecting to",self.app.ser_com.actual_port)
        self.test_dialog.title = "Valor actual en lectura: "
        self.app.ser_com.open_and_write(command)
        #print("Sending command")
        self.reception_event = Clock.schedule_interval(
            partial(self.data_reception, self.data_list), 0.01)  # Iniciar bucle de lectura

    def data_reception(self, data_list, *largs):
        """Lectura de una línea de datos."""
        # print("Reading")
        self.test_dialog.title = f"Valor actual en lectura: {self.app.ser_com.actual_val}"
        self.do_reception = self.app.ser_com.receive_data(data_list)
        if not self.do_reception:
            self.app.ser_com.arduino_ser.close()
            self.save_data(data_list)
            self.enable_buttons_back()
            self.test_dialog.title = "Los datos se han almacenado con éxito."
            return False

    def save_data(self, data_list):
        print(data_list)
        today = date.today()
        today_str = today.strftime("%d/%m/%Y")

        self.app = MDApp.get_running_app()
        db_data = self.app.current_user_data

        sensor_data_dict = json.loads(db_data[9 - self.current_sensor])
        try:
            samples = sensor_data_dict[today_str].keys()
            samples_num = map(lambda x: int(x),samples)
            max_sample = max(samples_num)
            sensor_data_dict[today_str][f"{max_sample + 1}"] = data_list
        except KeyError:
            sensor_data_dict[today_str] = {}
            sensor_data_dict[today_str]["1"] = data_list

        json_str = json.JSONEncoder().encode(sensor_data_dict)
        self.app.current_user_data[9 - self.current_sensor] = json_str
        db.edit_patient(*self.app.current_user_data)



class DisplayResultsWindow(Screen):
    def on_enter(self, *args):
        super().on_enter(*args)
        self.app = MDApp.get_running_app()
        index = 7 if self.sample_data == "rot" else 8
        data_dict = json.loads(self.app.current_user_data[index])
        data = data_dict[self.current_date][self.sample_num]

        if self.sample_data =="acc":
            data = list(map(lambda x: x - data[0],data))

        self.label = "Aceleración" if self.sample_data=="acc" else "Velocidad angular"
        label_opt = {"color": (0, 0, 0, 1)}
        print(type(data))
        self.samples = len(data)
        self.graph = Graph(label_options=label_opt,xmin=0, xmax=self.samples * 0.06, ymin=min(data), ymax=max(data),
            xlabel='tiempo', ylabel=self.label,y_grid_label=True,x_grid_label=True, x_ticks_major=(len(data)*0.06)/5, y_ticks_major=max(data)/5, padding=5)
        self.ids.dr_topbar.title = self.current_date
        self.ids.dr_topbar.title += f", toma {self.sample_num} - {self.label}"
        self.ids.dr_box.add_widget(self.graph)
        self.plot_x = np.linspace(0, 1, self.samples)
        self.plot_y = np.array(data)
        print(self.plot_y)
        self.plot = MeshLinePlot(color=[1, 0, 0, 1])
        self.plot.points = [(x*0.06, self.plot_y[x]) for x in range(self.samples)]
        self.graph.add_plot(self.plot)
        time = 0
        if self.sample_data =="rot":
            lower = 0
            higher = 0
            for index, value in enumerate(data):
                if value > 35 or value < -35:
                    lower = index
                    break
            for index, value in enumerate(reversed(data)):
                if value > 35 or value < -35:
                    higher = index
                    break
            time = 0.15 * (higher - lower)
            data_abs = list(map(lambda x: abs(x),data))
            if time > 12 or max(data_abs) < 70:
                fog = "+"
            else:
                fog ="-"
            self.ids.dr_box.add_widget(MDLabel(text=f"Valor máximo: {max(data_abs)}\nTiempo de giro: {time}\nFOG:{fog}", pos_hint={"center_x": .5}, size_hint_x=.5))
        if self.sample_data == "acc":
            squared_data = map(lambda x: x**2,data)
            rms_value = (sum(squared_data)/len(data))**(1/2)
            if rms_value < 1.5:
                fog = "+"
            else:
                fog ="-"
            self.ids.dr_box.add_widget(MDLabel(text=f"RMS: {rms_value}\n\nFOG:{fog}", pos_hint={"center_x": .5}, size_hint_x=.5))

        

    def on_leave(self, *args):
        super().on_leave(*args)
        self.ids.dr_box.clear_widgets()

    def back(self, *args):
        self.app = MDApp.get_running_app()
        self.app.root.current = "dh_window"
        app.root.get_screen(
            "dh_window").manager.transition.direction = "right"

class DataHistoryWindow(Screen):
    def on_enter(self, *args):
        self.manager.transition.direction = "left"
        self.app = MDApp.get_running_app()
        self.data = "rot"
        now = datetime.now()
        now_str = now.strftime("%d/%m/%Y")
        self.current_date = now_str
        self.added_str = " - Datos de velocidad angular"
        
        super().on_enter(*args)
        Clock.schedule_once(self.update_page)

    def switch_data(self, x=None):
        if self.data == "rot":
            self.data = "acc"
            self.ids.data_button.text = "Velocidad angular"
            self.added_str = " - Datos de aceleración"
        else:
            self.data = "rot"
            self.ids.data_button.text = "Aceleración"
            self.added_str = " - Datos de velocidad angular"
        self.update_page()
        

    def update_page(self, x=None):
        self.app = MDApp.get_running_app()
        index = 7 if self.data == "rot" else 8
        data_dict = json.loads(self.app.current_user_data[index])
        self.ids.dh_list.clear_widgets()
        self.ids.dh_topbar.title = self.current_date if self.current_date != datetime.now().strftime("%d/%m/%Y") else "Hoy"
        self.ids.dh_topbar.title += self.added_str
        try:
            samples = data_dict[self.current_date]
            for key in samples:
                self.ids.dh_list.add_widget(
                    OneLineListItem(text=f"Toma {key}", on_release= self.enter_sample)
                )
        except KeyError:
            self.ids.dh_list.add_widget(
                    MDLabel(text="No se encontraron tomas este día.")
                )

    def enter_sample(self, x=None):
        print(x.text[-1])
        self.app.root.get_screen("dr_window").sample_num = x.text[-1]
        self.app.root.get_screen("dr_window").sample_data = self.data
        self.app.root.get_screen("dr_window").current_date = self.current_date
        self.app.root.current = "dr_window"


    def back(self):
        self.app = MDApp.get_running_app()
        self.app.root.current = "start_window"
        app.root.get_screen(
            "start_window").manager.transition.direction = "right"

    def on_save(self, instance, value, date_range):
        self.current_date = value.strftime("%d/%m/%Y")
        self.update_page()

    def on_cancel(self, instance, value):
        pass

    def show_date_picker(self):
        today = datetime.today()
        date_dialog = MDDatePicker(
            year=today.year, month=today.month, day=today.day)
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()


class FogMeterApp(MDApp):
    current_user_data = None
    current_sensor_data = None
    ser_com = SerialCom()

    def build(self):
        # Setting theme to my favorite theme
        kv_file = Builder.load_file('main.kv')
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"
        return kv_file


if __name__ == '__main__':
    app = FogMeterApp()
    app.run()
