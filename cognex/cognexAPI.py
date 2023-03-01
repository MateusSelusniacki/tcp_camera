import telnetlib
import schedule
import socket
import threading

local = True

class Cognex():
    content = ''

    def __init__(self):
        self.title = 'camera'

    def receive(self,port):
        if(local):
            self.connect('172.31.1.55',port)
            print('not local connection')
        else:
           self.connect('localhost',port)

        print('waiting to receive from camera')
        self.content = self.client.recv(8192).decode()

        self.content = self.content.replace('\r\n','')

        print('disconnect')
        self.disconnect()
    
    def connect(self,ip,port):
        try:
            print(f'connecting {ip} {port}')
            self.client = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
            self.conn = self.client.connect( ( ip, port ) )

            return 1
        except Exception as E:
            print(E)
            return 0

    def disconnect(self):   
        try:
            self.client.close()
        except Exception as E:
            print(E)
            return

    def send(self,data):
        self.client.send(data.encode())

    def command(self,host,port, command):
        #definindo timeout
        timeout = 2

        #usuario e senha
        user = 'admin'
        password = ''

        #inicia conexão via ip
        tn = telnetlib.Telnet(host)

        #open no ip e porta
        tn.open(host,port, timeout)

        #insere o usuario
        tn.read_until(b"User:")
        tn.write(user.encode('ascii') + b"\r\n")

        #insere a senha
        tn.read_until(b"Password:")
        tn.write(password.encode('ascii') + b"\r\n")

        #envia o comando de trigger (se8)
        tn.read_until(b"Logged")
        tn.write(command.encode('ascii') + b"\r\n")

        #finaliza a conexão
        tn.close()

    def trigger(self,ip = '172.31.1.55',port = 23):
        self.command(ip,port,'SE8')

    def load_file(self,filename,ip = '172.31.1.55',port = 23):
        self.command(ip,port,"LF"+filename)

    def setOnline(self,ip = '172.31.1.55',port = 23):
        self.command(ip,port,'SO1')

    def setOffline(self,ip = '172.31.1.55',port = 23):
        self.command(ip,port,'SO0')

if __name__ == '__main__':
    camera = Cognex()
    #camera.command('172.31.1.55',23,"LFteste_kuka.job")
    camera.trigger('172.31.1.55',23)
    #setOffline()
    #setOnline()