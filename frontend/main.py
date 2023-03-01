from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import Screen
 
class Demo(MDApp):
    def build(self):
        self.screen = Screen()
         
        self.l1 = MDLabel(
            text = "My Label"
        )

        self.screen.add_widget(self.l1)
        return self.screen 
 
if __name__ == "__main__":
    Demo().run()