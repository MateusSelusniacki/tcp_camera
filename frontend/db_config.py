from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.button import MDIconButton
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import Screen
from kivymd.theming import ThemeManager
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField, MDTextFieldRect
from kivymd.uix.card import MDCard

from filechoose import FileChooser
import threading

from functools import partial
import sys

sys.path.append("..")

from erro.popErro import Error_Handle
from db.db import DB
import log_gen.log_sys as log

database = DB()

Window.maximize()

class db_config(Screen,MDApp):
    e_err = Error_Handle()
    families = database.Select("family")
    not_removeBtnUpdate = None
    path = None

    def __init__(self,**kwargs):
        super(db_config,self).__init__(**kwargs)
        log.logPrint("Iniciando painel de administrador")
        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = "Blue"

        self.btn_back = MDRectangleFlatButton(
            text = "<",
            pos_hint = {"center_x":0.1,"center_y":0.9},
            on_press = self.GoBack
        )
        self.btn_new = MDRectangleFlatButton(
            text = "+",
            pos_hint = {"center_x":0.25,"center_y":0.8},
            on_press = self.New
        )
        self.btn_insert = MDRectangleFlatButton(
            text = "INSERIR",
            pos_hint = {"center_x":0.74,"center_y":0.8},
            on_press = self.Insert
        )
        self.tf_insert_partnumber = MDTextField(
            pos_hint = {"center_x":0.36,"center_y":0.8},
            size_hint = (0.15,0.1)
        )
        self.tf_insert_familia = MDTextField(
            pos_hint = {"center_x":0.52,"center_y":0.8},
            size_hint = (0.15,0.1)
        )
        self.folder_insert = MDIconButton(
                icon="folder",
                pos_hint = {"center_x":0.64,"center_y":0.79},
                on_press = self.fileSelector
        )
        self.lbl_insert_partnumber = MDLabel(
            text = "Part Number",
            pos_hint = {"center_x":0.79,"center_y":0.83}
        )
        self.lbl_insert_familia = MDLabel(
            text = "Familia",
            pos_hint = {"center_x":0.95,"center_y":0.83},
        )
        self.lbl_insert_folder = MDLabel(
            text = "Arquivo/Template",
            pos_hint = {"center_x":1.1,"center_y":0.83}
        )
        self.lbl_update_familia = MDLabel(
            text = "Familia",
            pos_hint = {"center_x:"}
        )

        self.layout = GridLayout(cols=5, 
            spacing=10, 
            size_hint_y=None, 
            padding = [300,0,0,0]
            )
        # Make sure the height is such that there is something to scroll.
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.layout.add_widget(MDLabel(text = "PART NUMBER",bold = True,size_hint_y=None))
        self.layout.add_widget(MDLabel(text = "FAMILIA",bold = True,size_hint_y=None))
        self.layout.add_widget(MDLabel(text = "ARQUIVO",bold = True,size_hint_y=None))
        self.layout.add_widget(MDLabel(text = "EDITAR",bold = True,size_hint_y=None))
        self.layout.add_widget(MDLabel(text = "EXCLUIR",bold = True,size_hint_y=None))

        self.partnumber = []
        self.family = []
        self.folder = []
        self.edit = []
        self.delete = []

        self.row = 0
        self.rows_map = dict()

        for i in database.Select("part_number"):
            self.row_inserting(i)

        self.scroll = ScrollView(size_hint=(1, None), size=(Window.width-250, Window.height-200))
        
        self.scroll.add_widget(self.layout)

        self.add_widget(self.scroll)
        self.add_widget(self.btn_new)
        self.add_widget(self.btn_back)

        Window.bind(mouse_pos = self.posMouse)

    def row_inserting(self,i):
        self.partnumber.append(MDLabel(
            text = i[1]
        ))
        self.family.append(MDLabel(
            text = i[2]
        ))
        self.folder.append(MDIconButton(
            icon="folder",
            on_press = partial(self.update_fileSelector,i)
        ))
        self.edit.append(MDIconButton(
            icon="tooltip-edit",
            on_press = partial(self.btn_update,self.row)
        ))
        self.delete.append(MDIconButton(
            icon="trash-can",
            on_press = partial(self.btn_delete,self.row)
        ))

        self.rows_map[i[1]] = self.row

        self.layout.add_widget(self.partnumber[self.row])
        self.layout.add_widget(self.family[self.row])
        self.layout.add_widget(self.folder[self.row])
        self.layout.add_widget(self.edit[self.row])
        self.layout.add_widget(self.delete[self.row])

        self.row += 1

    def fileSelector(self,args):
        dialog = FileChooser()
        path = dialog.open_file()
        
        self.path = path[0]

    def update_fileSelector(self,tup,btn):
        print('tup',tup)
        log.logPrint(f"Atualizando arquivo {tup}")
        dialog = FileChooser()
        path = dialog.open_file()

        if(path == []):
            log.logPrint("Arquivo não atualizado")
            return -1

        database.Update_part_number_template(path[0],tup[1])
        print('arquivo atualizado',path[0],tup[1])
        log.logPrint(f"Arquivo atualizado {path[0]}")
        return 1

    def Insert(self,btn):
        family = self.tf_insert_familia.text
        partnumber = self.tf_insert_partnumber.text

        if(family == "" or partnumber == ""):
            self.e_err.layout_popup("ERRO","Preencha todos os campos")
            return -1
        
        if(self.path == None):
            self.e_err.layout_popup("ERRO","Escolha um arquivo de template")
            return -1
        
        val = self.path.split(".")[1]
        if(val != "ezd"):
            self.e_err.layout_popup("ERRO",f"Template escolhido não é válido")
            return -1
        
        for i in self.families:
            if(i[1] == family):
                rc = database.Insert_part_number((partnumber,self.path,family))
                self.tf_insert_familia.text = ""
                self.tf_insert_partnumber.text = ""
                self.path = None

                self.New()

                if(rc != 1):
                    self.e_err.layout_popup("ERRO","Erro ao inserir o part number")

                self.row_inserting((1,partnumber,family))
                log.logPrint(f"Novo partnumber inserido {partnumber} com familia {family}")
                return 1

        self.e_err.layout_popup("ERRO","Familia não encontrada")
        return -1

    def New(self,btn = None):
        if(self.btn_new.text == "+"):
            self.btn_new.text = "-"
            self.add_widget(self.btn_insert)
            self.add_widget(self.tf_insert_partnumber)
            self.add_widget(self.tf_insert_familia)
            self.add_widget(self.folder_insert)
            self.add_widget(self.lbl_insert_partnumber)
            self.add_widget(self.lbl_insert_familia)
            self.add_widget(self.lbl_insert_folder)
        else:
            self.btn_new.text = "+"
            self.path = None
            self.remove_widget(self.btn_insert)
            self.remove_widget(self.tf_insert_partnumber)
            self.remove_widget(self.tf_insert_familia)
            self.remove_widget(self.folder_insert)
            self.remove_widget(self.lbl_insert_partnumber)
            self.remove_widget(self.lbl_insert_familia)
            self.remove_widget(self.lbl_insert_folder)

    def btn_update(self,row,btn):
        tup = (1,self.partnumber[row].text,self.family[row].text)
        self.not_removeBtnUpdate = True
        try:
            print('removing updateCard in btn_update')
            self.remove_widget(self.updateCard)
        except:
            print('not removing updateCard in btn_update')
            pass

        print("tup",tup)
        layout_pos = self.mouse
        print(layout_pos)

        self.updateCard = MDCard(
            line_color=(0.2, 0.2, 0.2, 0.8),
            style="outlined",
            md_bg_color= "#FDFDFD",
            #shadow_softness=12,
            #shadow_offset=(0, 2),
            size_hint = (None,None),
            size = (350,280),
            pos = (layout_pos[0],layout_pos[1]-280) 
        )

        if(layout_pos[1] < 280):
            self.updateCard.pos = (layout_pos[0],0)

        Grid = GridLayout(cols = 1,size_hint_y=None,pos_hint = {"center_x":0.1,"center_y":0.7},spacing = [10,20],padding = [30,0,30,0])

        self.update_part_number = MDTextFieldRect(
                text = tup[1],
                size_hint = (1,None),
                halign = "center",
                height = 30
            )

        self.update_family = MDTextFieldRect(
                text = tup[2],
                size_hint = (1,None),
                halign = "center",
                height = 30
            )

        Grid.add_widget(
            MDLabel(
                text = "PART NUMBER",
                theme_text_color="Custom",
                text_color= (.50,.70,1,1),
                bold = True,
                halign = "center",
            )
        )

        Grid.add_widget(
            self.update_part_number
        )

        Grid.add_widget(
            MDLabel(
                text = "FAMILIA",
                theme_text_color="Custom",
                text_color= (.50,.70,1,1),
                bold = True,
                halign = "center",
            )
        )

        Grid.add_widget(
            self.update_family
        )

        btns_Grid = GridLayout(cols = 2,padding = [0,15,0,0],spacing = [20,10])
        btns_Grid.add_widget(
            MDRectangleFlatButton(
                text = "Atualizar",
                halign = "center",
                padding = [40,0,40,0],
                on_press = partial(self.btn_setPartNumber,tup[1])
            )
        )

        btns_Grid.add_widget(
            MDRectangleFlatButton(
                text = "Cancelar",
                halign = "center",
                padding = [40,0,40,0],
                on_press = self.btn_cancel
            )
        )
        Grid.add_widget(btns_Grid)
        print('update card added')
        self.updateCard.add_widget(Grid)
        self.add_widget(self.updateCard)

    def btn_delete(self,row,btn):
        def remove_widget(self,Card,btn):
            self.remove_widget(Card)

        def delete_this(self,row,btn):
            tup = self.partnumber[row].text
            print("tup",tup)
            database.Delete_Part_number((tup,))
            log.logPrint(f"Partnumber deletado {tup}")
            row2del = self.rows_map[tup]
            self.layout.remove_widget(self.partnumber[row2del])
            self.layout.remove_widget(self.family[row2del])
            self.layout.remove_widget(self.folder[row2del])
            self.layout.remove_widget(self.edit[row2del])
            self.layout.remove_widget(self.delete[row2del])

            self.remove_widget(Card)

        print('btn_delete')
        Card = MDCard(
            line_color=(0.2, 0.2, 0.2, 0.8),
            style="outlined",
            md_bg_color= "#FDFDFD",
            #shadow_softness=12,
            #shadow_offset=(0, 2),
            size_hint = (None,None),
            size = (300,180),
            pos_hint = {"center_x":0.5,"center_y":0.5} 
        )
        Grid = GridLayout(cols = 1,size_hint_y=None,pos_hint = {"center_x":0.1,"center_y":0.4},spacing = [15,50],padding = [20,0,20,0])
        Card.add_widget(Grid)

        Grid.add_widget(
            MDLabel(
                text = f"Tem Certeza Que Deseja Excluir o Part Number {self.partnumber[row].text}?",
                theme_text_color="Custom",
                text_color= (.40,.50,1,1),
                bold = True,
                halign = "center"
            )
        )
        
        SubGrid = GridLayout(cols = 2,size_hint_y=None,spacing = [5,0],padding = [50,0,50,0])
        Grid.add_widget(SubGrid)

        SubGrid.add_widget(
            MDRectangleFlatButton(
                text = "Confimar",
                on_press = partial(delete_this,self,row)
            )
        )
        
        SubGrid.add_widget(
            MDRectangleFlatButton(
                text = "Cancelar",
                on_press = partial(remove_widget,self,Card)
            )
        )

        self.add_widget(Card)

    def btn_cancel(self,btn):
        self.remove_widget(self.updateCard)
    
    def btn_setPartNumber(self,old_number,btn):
        print("update")
        log.logPrint("Atualizando partnumber")
        family = self.update_family.text
        part_number = self.update_part_number.text
        if(family == "" or part_number == ""):
            self.e_err.layout_popup("ERRO","Preencha todos os campos")

        for i in self.families:
            if(i[1] == family):
                rc = database.Update_part_number((old_number,"familia"),(part_number,family))
                if(rc != 1):
                    self.e_err.layout_popup("ERRO","Erro ao inserir o part number")
                    return -1

                self.remove_widget(self.updateCard)
                row = self.rows_map[old_number]
                self.rows_map[part_number] = row

                self.partnumber[row].text = part_number
                self.family[row].text = family
                log.logPrint(f"Partnumber atualizado {self.partnumber[row].text} {self.family[row].text}")
                return 1

        self.e_err.layout_popup("ERRO","Familia não encontrada")
        return -1

    def GoBack(self,btn):
        log.logPrint("Saindo do painel de administrador")
        self.manager.transition.direction = 'right'
        self.manager.current = 'main_screen'

    def posMouse(self,btn,pos):
        self.mouse = pos