
from ctypes import c_bool, c_double, c_int, c_wchar_p, c_uint16, WinDLL, byref
import os

class Laser():
    dll = '..\\ezcad\\Ezcad2.14.11-SDK\\MarkEzd.dll'
    sdk_path = '..\\ezcad\\Ezcad2.14.11-SDK\\'

    erro_list = {
                "1":"Ezcad está aberto",
                "2":"Não foi possível abrir CFG",
                "3":"Não foi possível iniciar a placa",
                "4":"Dispositivo inválido",
                "5":"Versão do disposítivo inválida",
                "6":"Não foi possível encontrar arquivo de configuração",
                "7":"Sinal de Parada",
                "8":"Interrupção pelo Usuário",
                "9":"Erro Desconhecido",
                "10":"Tempo limite",
                "11":"Não inicializado",
                "12":"Erro de leitura de arquivo",
                "13":"Janela Nula",
                "14":"Font não encontrada",
                "15":"Número de caneta inválida",
                "16":"Objeto não é texto",
                "17":"Falha ao Salvar",
                "18":"Não foi encontrado o objeto",
                "19":"Impossível realizar a operação no estado atual"
    }

    def __init__(self):
        self.connect()
    
    def connect(self):
        self.pathc = c_wchar_p(self.sdk_path) 

        try:
            self.libc = WinDLL(self.dll)
        except:
            print('Não foi possível carregar dll')
            return -1
        
        print('dll carregada')
        
        rc = self.libc.lmc1_Initial(self.pathc, c_bool(False),c_int(0))
        
        if(not rc):
            print('Laser conectado')
            return 1
        else:
            print(f"Não foi possível se conectar com o laser {rc}")
            return -1

    def load_template(self,template):
        self.template = c_wchar_p(template) 
        rc = self.libc.lmc1_LoadEzdFile(self.template)

        if(not rc):
            print('template carregado')
            return 1
        else:
            print(f'Não foi possivel carregar o template. rc = {rc}')
            raise Exception(self.erro_list[str(rc)])
            return rc

    def saveFile(self):
        rc = self.libc.lmc1_SaveEntLibToFile(self.template)

        if(rc):
            print("Não foi possível salvar")
            raise Exception(self.erro_list[str(rc)])
        return 1
    
    def Mark(self,
        bFlyMark = 0
        ):
        rc = self.libc.lmc1_Mark(c_bool(bFlyMark))
        if(rc):
            pritn("Não foi possível gravar")
            raise Exception(self.erro_list[str(rc)])
        return rc

    def close(self):
        self.libc.lmc1_Close()

'''
laser = Laser()
laser.load_template("./teste.ezd")
laser.Mark()
'''