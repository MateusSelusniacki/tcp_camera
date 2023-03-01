import kivy

from kivymd.app import MDApp

from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

import main_screen
import db_config

import os
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'

import sys

#sys.stdout = open("saidas","a")

class ScreenManagement(ScreenManager):
    def __init__(self, **kwargs):
        super(ScreenManagement, self).__init__(**kwargs)

class App(MDApp):   
    def build(self):
        self.screen_manager = ScreenManagement(transition=SlideTransition())
        self.screen_manager.add_widget(main_screen.main_screen(name = "main_screen"))
        self.screen_manager.add_widget(db_config.db_config(name = "db_config"))

        return self.screen_manager

if __name__ == '__main__':
    App().run() 