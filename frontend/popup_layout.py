
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

def layout_popup(mensagem,title,btn,args = None):
    layout = GridLayout(cols = 1, padding = 10)
    popupLabel = MDLabel(
        text = mensagem,
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
    
    popup = Popup(title =title,
                    content = layout,
                    size_hint =(None, None),
                    size =(200, 200))
                    
    closeButton = MDRectangleFlatButton(text = "Fechar",
        pos_hint = {"center_x":0.5,"center_y":0.5},
        size_hint=  (1, None),
        on_press = popup.dismiss)

    layout.add_widget(closeButton)

    popup.open()  

'''class demo(MDApp):
    def build(self):
        x = "mensagem"
        return MDRectangleFlatButton(text = "texto",
            on_press = partial(layout_popup,"mensagem","Erro"))

demo().run()'''