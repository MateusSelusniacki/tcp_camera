import datetime

def logPrint(message):
    f = open("..\\logfile.txt", "a")
    f.write(f"{str(datetime.datetime.now())} {message}\n")
    f.close()