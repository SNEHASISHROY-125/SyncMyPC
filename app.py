from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen

import os

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.toast import toast
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.transition import MDSwapTransition, MDFadeSlideTransition, MDSlideTransition

from kivy.core.window import Window
from kivy.core.image import Image


KV = '''

MDScreenManager:
    id: smanager
    
    MDScreen:
        id: mainS
        name: "main"
        MDRaisedButton:
            pos_hint: {"center_x": .5, "center_y": .5}
            on_release: app.file_manager_open()
            text: "Select folder location"
    MDScreen:
        name: "server"
        MDRaisedButton:
            pos_hint: {"center_x": .5, "center_y": .5}
            on_release: app.start_server()
            text: "Start Server"
        
        MDRaisedButton:
            pos_hint: {"center_x": .5, "center_y": .7}
            on_release: app.get_server_stats()
            text: "Get Server Stats"
        MDRaisedButton:
            pos_hint: {"center_x": .5, "center_y": .8}
            on_release: app.change_server_stats()
            text: "Close Server"
    
'''

class SManager(MDScreenManager):...

class Example(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path,
            # preview=True,
            icon_selection_button="pencil",
        )

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.sm = Builder.load_string(KV)
        
        self.sm.transition = MDSwapTransition()
        return self.sm
    
    def file_manager_open(self):
        self.file_manager.show(
            os.path.expanduser("~"))  # output manager to the screen
        self.manager_open = True

    def select_path(self, path: str):
        '''
        It will be called when you click on the file name
        or the catalog selection button.

        :param path: path to the selected directory or file;
        '''

        self.exit_manager()
        # self.MDScreenManager.get_screen('main').add_widget(Label(text=path))
        self.sm.current = 'server'
        global selec_path
        selec_path = path
        toast(selec_path)
        # MDSnackbar(
        #     # MDSnackbarText(
        #     text=path
        #     ,
        #     y=dp(24),
        #     pos_hint={"center_x": 0.5},
        #     size_hint_x=0.8,
        # ).open()

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def start_server(self):
        self.sm.current ='main'
        toast('path selected'+' '+selec_path)
        #interact with server
    def get_server_stats(self):
        toast(str(s.memry_dict['server_running']))
    def change_server_stats(self):
        s.memry_dict['server_running'] = False
        toast('server closed')
        #interact with server


# importing server.py makes everything be present in same memory
import server as s

# starts server in seperate thread, making its server-api be accesable through memry_dict{} (global) in app.py
s.start_server()

global selec_path
selec_path = ''

Example().run()