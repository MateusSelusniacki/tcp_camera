from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import Screen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock    
from kivy.core.window import Window
from kivymd.theming import ThemeManager
from kivy.config import Config  
from kivy.uix.image import Image
from kivy.clock import Clock

import time
import threading
import sys
from functools import partial

sys.path.append("..")

from erro.popErro import Error_Handle
from db.db import DB
from cognex.cognexAPI import Cognex
from ezcad.laser import Laser
import log_gen.log_sys as log

Window.maximize()

class main_screen(Screen):
    title = 'Tela Principal'
    logincardon = 0
    success = 0
    event = threading.Event()

    def __init__(self,**kwargs):
        super(main_screen,self).__init__(**kwargs)
        Window.bind(on_key_down=self._on_keyboard_down)
        log.logPrint('Software iniciado')

        Clock.schedule_once(self.init_back_end,2)

        self.theme_cls = ThemeManager()
        self.theme_cls.primary_palette = "Blue"

        self.success_card()

        self.PROMarking_Image = Image(
            source = "imagens/promarking_vertical_positivo_resize.png",
            pos_hint = {"center_x":0.5,"center_y":0.7}
        )
        self.partNumber_tf = MDTextField(
            pos_hint = {"center_x":0.5,"center_y":0.35},
            size_hint = (0.3,0.5),
            halign = 'center',
            foreground_color= (.20,.30,1,1),
        )
        self.partNumber_label = MDLabel(
            text = "PART NUMBER",
            pos_hint = {"center_x":0.96,"center_y":0.4},
            theme_text_color="Custom",
            text_color = (.20,.30,1,1),
            bold = True
        )
        self.db_config = MDIconButton(
            icon = "key-chain",
            pos_hint = {"center_x": .9,"center_y":0.9},
            on_release = self.go2config
        )

        self.new_batch = MDRectangleFlatButton(
            text = "Novo Lote",
            halign = "center",
            pos_hint = {"center_x":0.5,"center_y":0.25},
            on_release = self.btnStart
        )

        self.add_widget(self.PROMarking_Image)
        self.add_widget(self.partNumber_label)
        self.add_widget(self.partNumber_tf)
        self.add_widget(self.db_config)
        self.add_widget(self.new_batch)
        self.AuthCard()

        self.partNumber_tf.focus = True

    '''def on_focus(self,instance,value):
        self.passwordTF.text = ""
    '''

    def vbtn(self,btn):
        print(self.database.get_fileByPartNumber(self.partNumber_tf.text))

    def init_back_end(self, *largs):
        self.e_err = Error_Handle()
        self.database = DB()
        
        self.camera = Cognex()

        self.laser = Laser()

    def add(self, *largs):
        self.add_widget(self.SuccessCard)
    
    def remove(self, *largs):
        self.remove_widget(self.SuccessCard)

    def erroOnThread(self,arg1,arg2, *largs):
        self.e_err.layout_popup(arg1,arg2)

    def btnStart(self, btn = None):
        if(self.new_batch.text == "Começar"):
            print('começar')
            self.new_batch.text = "Novo Lote"
            self.partNumber_tf.disabled = True
            partNumber = self.partNumber_tf.text
            if(partNumber == ""):
                self.e_err.layout_popup("ERRO","Preencha o campo PART NUMBER")
                self.new_batch.text = "Começar"
                self.partNumber_tf.disabled = False
                return 0
            else:
                if(not self.database.partNumberExists(partNumber)):
                    self.e_err.layout_popup("ERRO","PART NUMBER não encontrado")
                    self.new_batch.text = "Começar"
                    self.partNumber_tf.disabled = False
                    return 0
                
                print('PART_NUMBER_OK')

                family = self.database.get_familyByPartNumber(partNumber)
                if(not self.database.familyExists(family)):
                    print(f"familia |{type(family)}|")
                    self.e_err.layout_popup("ERRO","Familia do PART NUMBER não encontrada")
                    self.new_batch.text = "Começar"
                    self.partNumber_tf.disabled = False
                    return 0

                print('PART_NUMBER_FAMILY_OK')
                
                print(family)
                try:
                    self.camera.setOffline()
                    self.camera.load_file(family + ".job")
                    self.camera.setOnline()
                    time.sleep(6)
                    log.logPrint('Job Carregado')
                    print('job carregado')
                except:
                    print('erro com a camera')
                    self.e_err.layout_popup("ERRO","Falha com a camera - FILE LOAD")
                    self.new_batch.text = "Começar"
                    self.partNumber_tf.disabled = False
                    return 0
                
                print("JOB_LOAD_OK")

                try:
                    file = self.database.get_fileByPartNumber(partNumber)
                    print(file)
                except:
                    log.logPrint('Falha ao carregar template do laser no banco de dados')
                    self.e_err.layout_popup("ERRO","Falha ao carregar template do banco de dados")
                    self.new_batch.text = "Começar"
                    self.partNumber_tf.disabled = False
                    return 0

                try:
                    print(f'loading template {file}')
                    self.laser.load_template(file)
                    log.logPrint('Template do laser carregado')
                except Exception as e:
                    self.e_err.layout_popup("ERRO",f"Falha ao carregar template para gravação - {e}")
                    self.new_batch.text = "Começar"
                    self.partNumber_tf.disabled = False
                    return 0
            #threading.Thread(target = self.returnHandler()).start()
            self.event.set()
            self.process = threading.Thread(target = self.returnHandler, daemon = True)
            self.process.start()
                
        elif(self.new_batch.text == "Novo Lote"):
            log.logPrint("novo lote")
            self.partNumber_tf.disabled = False
            self.event.clear()
            self.camera.disconnect()
            self.new_batch.text = "Começar"
        else:
            print('nothing to do with this button click')
            pass
        
    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40:
            if(self.partNumber_tf.focus == True):
                print('-partnumber focus')
                self.btnStart()
                return
            if(self.passwordTF.focus == True):
                print('password focus')
                self.auth()
                return

    def success_card(self):
        self.SuccessCard = MDCard(
            line_color=(0.2, 0.2, 0.2, 0.8),
            style="outlined",
            md_bg_color= "#FDFDFD",
            #shadow_softness=12,
            #shadow_offset=(0, 2),
            size_hint = (None,None),
            size = (100,80),
            pos_hint = {"center_x":0.5,"center_y":0.5} 
        )

        self.SuccessCard.add_widget(
            MDLabel(
                text = "Sucesso",
                theme_text_color="Custom",
                text_color= (.20,.30,1,1),
                bold = True,
                halign = "center"
            )
        )
    
    def cameraOk(self,port,proc):
        try:
            self.camera.receive(port)
            if(self.camera.content == "ok"):
                print("ok")
                log.logPrint('Peça ok')
                return 1
            else:
                Clock.schedule_once(partial(self.erroOnThread,"Erro","Camera não ok"),0.5)
                print(f"nok {self.camera.content}") 
                return 0
        except Exception as e:
            print(e)
            Clock.schedule_once(partial(self.erroOnThread,"Erro","Camera não ok"),0.5)

    def returnHandler(self):
        while(self.event.is_set()):
            log.logPrint("Esperando a camera")
            if(not self.cameraOk(53123,"reconhecimento de peça")):
                continue
            print('saiu da camera')
            try:
                rc = self.laser.Mark()
                print(f'mark {rc}')
                log.logPrint(f"Gravação realizada - rc = {rc}")
            except:
                self.e_err.layout_popup("ERRO","Falha ao realizar gravação")
                continue 

            '''if(not self.cameraOk(53124,"reconhecimento de datamatrix")):
                return 0'''
            
            try:
                print(f'saving laser file {self.laser.saveFile()}')
                log.logPrint('Arquivo do laser salvo')
            except:
                Clock.schedule_once(partial(self.erroOnThread,"ATENÇÃO","O arquivo não pode ser salvo"),0.5)

            print(f'final do ciclo')
            log.logPrint('Sucesso na gravação')
            self.success = 1
            Clock.schedule_once(self.add,0.5)

            Clock.schedule_once(self.remove,2.5)

            self.partNumber_tf.focus = True

    def AuthCard(self):
        self.Card = MDCard(
            line_color=(0.2, 0.2, 0.2, 0.8),
            style="outlined",
            md_bg_color= "#FDFDFD",
            #shadow_softness=12,
            #shadow_offset=(0, 2),
            size_hint = (None,None),
            size = (350,320),
            pos_hint = {"center_x":0.5,"center_y":0.5} 
        )

        Grid = GridLayout(cols = 1,size_hint_y=None,pos_hint = {"center_x":0.1,"center_y":0.7},spacing = [15,50],padding = [20,0,20,0])
        self.Card.add_widget(Grid)

        Grid.add_widget(
            MDLabel(
                text = "LOGIN",
                theme_text_color="Custom",
                text_color= (.20,.30,1,1),
                bold = True,
                halign = "center"
            )
        )

        SubGrid = GridLayout(cols = 2,size_hint_y=None,spacing = [5,2],padding = [50,0,80,0])
        Grid.add_widget(SubGrid)

        self.userTF = MDTextField()
        self.passwordTF = MDTextField(
            password = True
        )
        #self.passwordTF.bind(focus=self.on_focus)

        SubGrid.add_widget(
            MDLabel(
                text = "Usuário:",
                theme_text_color="Custom",
                text_color= (.40,.60,1,1),
                bold = True,
                halign = "center",
                valign = "bottom"
            )
        )
        SubGrid.add_widget(
            self.userTF
        )
        SubGrid.add_widget(
            MDLabel(
                text = "Senha:",
                theme_text_color="Custom",
                text_color= (.40,.60,1,1),
                bold = True,
                halign = "center",
                valign = "bottom"
            )
        )
        SubGrid.add_widget(
            self.passwordTF
        )
        SubGrid.add_widget(
            MDLabel(
                markup = True,
                text = "[ref=reference]trocar senha[/ref]",
                on_ref_press = self.changePassword,
                theme_text_color="Custom",
                text_color= (.10,.20,1,1),
            )
        )
        SubGrid.add_widget(
            MDLabel(
                text = "",
                size_hint_y = None,
                height = 20
            )
        )
        SubGrid.add_widget(
            MDRectangleFlatButton(
                text = "Confimar",
                on_release = self.auth
            )
        )
        SubGrid.add_widget(
            MDRectangleFlatButton(
                text = "Cancelar",
                on_release = self.cancel_auth
            )
        )

    def newPass(self,btn):
        if(self.currentTF.text == "" and self.new2TF.text == "" and self.newTF.text == ""):
            self.e_err.layout_popup("ERRO","Preencha Todos os Campos")
            return -1

        if(self.new2TF.text != self.newTF.text):
            self.e_err.layout_popup("ERRO","Senhas Precisam Ser Iguais")
            return -1

        self.database.Update_Superuser(("admin",self.newTF.text))
        log.logPrint("Senha atualizada")

        self.currentTF.text = ""
        self.new2TF.text = ""
        self.newTF.text = ""

        self.remove_widget(self.changePassCard)

    def cance_newPass(self,btn):
        self.remove_widget(self.changePassCard)

    def changePassword(self,btn,ref):
        log.logPrint("Iniciando tela de troca de senha")
        self.changePassCard = MDCard(
            line_color=(0.2, 0.2, 0.2, 0.8),
            style="outlined",
            md_bg_color= "#FDFDFD",
            #shadow_softness=12,
            #shadow_offset=(0, 2),
            size_hint = (None,None),
            size = (350,350),
            pos_hint = {"center_x":0.5,"center_y":0.5} 
        )

        Grid = GridLayout(cols = 1,size_hint_y=None,pos_hint = {"center_x":0.1,"center_y":0.7},spacing = [15,50],padding = [20,0,20,0])
        self.changePassCard.add_widget(Grid)

        Grid.add_widget(
            MDLabel(
                text = "Trocar Senha",
                theme_text_color="Custom",
                text_color= (.20,.30,1,1),
                bold = True,
                halign = "center"
            )
        )

        SubGrid = GridLayout(cols = 2,size_hint_y=None,spacing = [5,2],padding = [40,0,40,0])
        Grid.add_widget(SubGrid)

        self.currentTF = MDTextField(password = True)
        self.newTF = MDTextField(password = True)
        self.new2TF = MDTextField(password = True)

        SubGrid.add_widget(
            MDLabel(
                text = "Senha Atual:",
                theme_text_color="Custom",
                text_color= (.40,.60,1,1),
                bold = True,
                halign = "center",
                valign = "bottom"
            )
        )
        SubGrid.add_widget(
            self.currentTF
        )
        SubGrid.add_widget(
            MDLabel(
                text = "Nova Senha:",
                theme_text_color="Custom",
                text_color= (.40,.60,1,1),
                bold = True,
                halign = "center",
                valign = "bottom"
            )
        )
        SubGrid.add_widget(
            self.newTF
        )
        SubGrid.add_widget(
            MDLabel(
                text = "Nova Senha Novamente:",
                theme_text_color="Custom",
                text_color= (.40,.60,1,1),
                bold = True,
                halign = "center",
                valign = "bottom"
            )
        )
        SubGrid.add_widget(
            self.new2TF
        )
        SubGrid.add_widget(
            MDRectangleFlatButton(
                text = "Confimar",
                on_release = self.newPass
            )
        )
        SubGrid.add_widget(
            MDRectangleFlatButton(
                text = "Cancelar",
                on_release = self.cance_newPass
            )
        )
        self.add_widget(self.changePassCard)

    def go2config(self,btn):
        log.logPrint("Iniciando tela de login")
        self.userTF.focus = True
        self.logincardon = 1
        self.add_widget(self.Card)
    
    def auth(self,btn = None):
        user = self.database.Select("Superuser")[0]
        if(not(user[1] == self.userTF.text and user[2] == self.passwordTF.text)):
            self.e_err.layout_popup("ERRO","Dados Inseridos Não São Válidos")
            log.logPrint("Usuário não autenticado")
            return -1

        log.logPrint("Usuário autenticado")
        self.userTF.text = ""
        self.passwordTF.text = ""

        self.manager.transition.direction = 'down'
        self.manager.current = 'db_config'
        self.logincardon = 0
        self.remove_widget(self.Card)

    def cancel_auth(self,btn = None):
        self.logincardon = 0
        self.remove_widget(self.Card)
