
# importing all necessary modules
# like MDApp, MDLabel Screen, MDTextField
# and MDRectangleFlatButton
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import Screen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton
from kivy.uix.gridlayout import GridLayout
from kivymd.theming import ThemeManager
from kivy.uix.popup import Popup

from functools import partial
import time
import log_gen.log_sys as log

class Error_Handle():
    def __init__(self):
        pass

    def layout_popup(self,title,mensagem,btn = None,args = None):
        layout = GridLayout(cols = 1, padding = 10)
        popupLabel = MDLabel(
            text = mensagem,
            bold = True,
            theme_text_color="Custom",
            text_color= (.14,.37,.60,1),
            halign = "center")

        layout.add_widget(popupLabel)

        if(args != None):
            for key in args:
                print(args[key]["type"])
                if(args[key]["type"] == "button"):
                    layout.add_widget(
                        Button(text = args[key]["text"],
                            on_press = args[key]["on_press"]
                        )
                    )
        
        self.popup = Popup(title =title,
                        title_color = (.14,.37,.60,1),
                        title_align = "center",
                        content = layout,
                        size_hint =(None, None),
                        size =(200, 200))
                        
        closeButton = MDRectangleFlatButton(text = "Fechar",
            pos_hint = {"center_x":0.5,"center_y":0.5},
            size_hint=  (1, None),
            on_press = self.popup.dismiss)

        layout.add_widget(closeButton)

        self.popup.open()  
        log.logPrint(mensagem)
    
    def popout(self):
        self.popup.dismiss()

'''class demo(MDApp):
    def build(self):
        layout_popup("mensagem","ERRO")
        return None

demo().run()'''

'''class demo(MDApp):
    def build(self):
        x = "mensagem"
        return MDRectangleFlatButton(text = "texto",
            on_press = partial(layout_popup,"mensagem","Erro"))

demo().run()'''