import sqlite3
from sqlite3 import Error
import pandas as pd

import sys
import os

sys.path.append("..")

deploy = False

class DB():
    def __init__(self):
        self.current_path = os.getcwd()
        if(not deploy):
            self.current_path = self.current_path.split('\\')
            self.current_path = '\\'.join(self.current_path[:-1])
        self.current_path += "\\db"

        if(not self.dbExists()):
            print('banco não existe')
            print('criando banco')
            self.generate_empty_db()
        else:
            self.db_file = self.current_path + "\\eaton.db"

        print(self.current_path)
        print(self.db_file)

    def dbExists(self):
        return os.path.exists(self.current_path + "\\eaton.db")

    def create_connection(self):
        """ create a database connection to a SQLite database """
        conn = None
        try:
            print(f'tentando criar conexão com {self.db_file} em {self.current_path}')
            conn = sqlite3.connect(self.db_file)
            return conn
        except Error as e:
            print(e)

    def generate_empty_db(self):
        try:
            self.db_file = self.current_path + "\\eaton.db"
            conn = self.create_connection()
            cursor = conn.cursor()

            cursor.execute("DROP TABLE IF EXISTS part_number")
            print("drop part_number table if exists")

            cursor.execute("DROP TABLE IF EXISTS family")
            print("drop family table if exists")

            cursor.execute("DROP TABLE IF EXISTS Superuser")
            print("drop Superuser table if exists")

            print("creating table part_number")
            cursor.execute("""
                CREATE TABLE part_number (
                    id	INTEGER NOT NULL UNIQUE,
                    part_number	TEXT NOT NULL UNIQUE,
                    family	TEXT NOT NULL,
                    file TEXT NOT NULL,
                    FOREIGN KEY(family) REFERENCES family,
                    PRIMARY KEY(id AUTOINCREMENT)
                );
            """)
            print("table part_number created")

            print("creating family part_number")
            cursor.execute("""
                CREATE TABLE family (
                    id	INTEGER NOT NULL UNIQUE,
                    family	TEXT NOT NULL UNIQUE,
                    PRIMARY KEY(id AUTOINCREMENT)
                );
            """)
            print("table family created")

            print("creating Superuser part_number")
            cursor.execute("""
                CREATE TABLE Superuser (
                    id	INTEGER NOT NULL UNIQUE,
                    user	TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL UNIQUE,  
                    PRIMARY KEY(id AUTOINCREMENT)
                );
            """)
            print("table Superuser created")
            
            df = pd.read_excel(self.current_path + './DiscosEaton.xlsx')

            print("inserting from DiscosEaton into family")
            for i in df['Familia (Modelo)']:
                self.Insert_family((i,))
            
            print("inserting from DiscosEaton into part_number")
            sub_df = df[['Item','Familia (Modelo)']]
            for i in sub_df.index:
                self.Insert_part_number((str(sub_df['Item'][i]),(self.current_path.replace('db','') + "templates\\" + str(sub_df['Item'][i]) + ".ezd"),sub_df['Familia (Modelo)'][i]))

            conn.close()

            print("Inserting Super user")
            self.Insert_user(("admin","MestreEaton"))
            print("Super user inserted")
            return 1
        except Error as e:
            print(f'Não foi possível terminar de criar o banco de dados {e}')
            return -1


    def Insert_user(self,tup):
        try:
            print(f'inserting user {tup[0]}')
            conn = self.create_connection()
            sql = ''' INSERT INTO Superuser (user,password)
                VALUES (?,?) '''
            cur = conn.cursor()
            cur.execute(sql, tup)
            conn.commit()
            return 1
        except Error as e:
            print(f'não foi possívle inserir usuário {e}')
            return -1

    def Insert_family(self,tup):
        print(f'Inserting family {tup[0]}')
        try:
            conn = self.create_connection()
            sql = ''' INSERT INTO family (family)
                VALUES (?) '''
            cur = conn.cursor()
            cur.execute(sql, tup)
            conn.commit()
            conn.close()
            print(f'Family {tup[0]} Inserted')
            return 1
        except Error as e:
            print(f"Não foi possível inserir a familia {e}")
            return -1

    def Insert_part_number(self,tup):
        try:
            print(f'Inserting part_number {tup[0]}')
            conn = self.create_connection()
            sql = ''' INSERT INTO part_number (part_number,file,family)
                VALUES (?,?,?) '''
            cur = conn.cursor()
            cur.execute(sql, tup)
            conn.commit()
            conn.close()
            print(f'Part_number {tup} Inserted')
            return 1
        except Error as e:
            print(f'não foi possível inserir part_number {e}')
            return -1

    def Select(self,table):
        try:
            print(f'Obtendo dados da tabela {table}')
            conn = self.create_connection()

            cur = conn.cursor()
            cur.execute(f'SELECT * FROM {table}')
            
            record = cur.fetchall()
            conn.close()
            print(f'dados obtidos')
            return record
        except Error as e:
            print(f'não foi possível obter os dados {e}')
            return ""
    
    def get_PartNumber(self):
        try:
            part_numbers = self.Select('part_number')
            
            return part_numbers
        except Error as e:
            print(f'não foi possível procurar o partNumber {e}')
            return None
    
    def partNumberExists(self,partNumber):
        part_numbers = self.get_PartNumber()
        if(part_numbers == None):
            print(f'Não foi possível encontrar nenhum partNumber')
            return None

        part_numbers = [x[1] for x in part_numbers]

        return partNumber in part_numbers

    def get_familyByPartNumber(self,partNumber):
        try:
            print(f'Procurando Familia do partNumber')
            part_numbers = self.Select('part_number')
            
            for i in part_numbers:
                if(i[1] == partNumber):
                    return i[2]
            return 0

        except Error as e:
            print(f'Erro {e}')
            return None
        
    def familyExists(self,family):
        try:
            print(f'Procurando {family}')
            families = self.Select('family')
            families = [x[1] for x in families]

            return family in families
        except:
            print(f'Erro ao verificar se familia existe {e}')
            return None

    def get_fileByPartNumber(self,partNumber):
        try:
            print(f'Procurando file do partNumber')
            part_numbers = self.Select('part_number')
            
            for i in part_numbers:
                if(i[1] == partNumber):
                    return i[3]
            return 0

        except Error as e:
            print(f'Erro {e}')
            return None

    def Update_Family(self,old_family,new_family):
        try:
            print(f'Updating family {old_family} to {new_family}')
            conn = self.create_connection()
            sql = ''' UPDATE family
                SET family = ?
                WHERE family = ?'''
            cur = conn.cursor()
            cur.execute(sql, (new_family,old_family))
            conn.commit()
            conn.close()
            print(f'Family {new_family} updated')
            return 1
        except Error as e:
            print(f'não foi possível atualizar familia {e}' )
            return -1

    def Update_part_number(self,old_number,new_number):
        try:
            print(f'Updating part_number {old_number} to {new_number}')
            conn = self.create_connection()
            sql = ''' UPDATE part_number
                SET part_number = ?, family = ?
                WHERE part_number = ?'''
            cur = conn.cursor()
            cur.execute(sql, (new_number[0],new_number[1],old_number[0]))
            conn.commit()
            conn.close()
            print(f'Part_number {new_number} updated')
            return 1
        except Error as e:
            print(f'não foi possível atualizar part_number {e}')
            return -1

    def Update_part_number_template(self,new_template,part_number):
        #try:
        print(f'Updating part_number {part_number} template to {new_template}')
        conn = self.create_connection()
        sql = '''UPDATE part_number
            SET file = ?
            WHERE part_number = ?'''
        cur = conn.cursor()
        cur.execute(sql, (new_template,part_number))
        conn.commit()
        conn.close()
        print(f'Part_number {part_number} updated')
        return 1
        '''except Error as e:
            print(f'não foi possível atualizar part_number {e}')
            return -1'''

    def Update_Superuser(self,new_user):
        try:
            conn = self.create_connection()
            sql = ''' UPDATE Superuser
                SET user = ?, password = ?
                WHERE id = 1'''
            cur = conn.cursor()
            cur.execute(sql, new_user)
            conn.commit()
            conn.close()
            return 1
        except Error as e:
            print(f'não foi possível trocar a senha de usuário {e}')
            return -1

    def Delete_Family(self,elem):
        try:
            print(f'Deleting {elem} from Family')
            conn = self.create_connection()
            sql = '''DELETE FROM family WHERE family = ?'''

            cur = conn.cursor()
            cur.execute(sql, elem)
            conn.commit()
            conn.close()
            print(f'Family {elem} deleted')
            return 1
        except Error as e:
            print(f"Não foi possível deletar a familia {e}")
            return -1
    
    def Delete_Part_number(self,elem):
        try:
            print(f'Deleting {elem} from part_number')
            conn = self.create_connection()
            sql = '''DELETE FROM part_number WHERE part_number = ?'''

            cur = conn.cursor()
            cur.execute(sql, elem)
            conn.commit()
            conn.close()
            print(f'part_numer {elem} deleted')
            return 1
        except Error as e:
            print(f'não foi possível deletar part_number {e}')
            return -1

if(__name__ == "__main__"):
    database = DB()
    print(database.dbExists())
#print(database.get_PartNumber("1281058"))

#database.generate_empty_db()
#database.Update_part_number_template('C:\\Users\\ti2\\OneDrive\\Documentos\\save.xml','1281056')
#database.Insert_part_number(("123456789","123456789.ezd","4 molas"))
#database.Delete_Part_number(("123456789",))
#database.Insert_family(("64 molas",))
#database.Delete_Family(("64 molas",))
#database.Update_Superuser(('mateus','password'))
#database.Update_part_number(('123456789','4 molas'),('1281056','4 molas'))