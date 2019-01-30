from __future__ import print_function
import serial
from base64 import b16encode, b16decode
import time


class Kobling: # Kommunikasjon mellom LinRS og python.
    def __init__(self, com_port):
        self.com_port = com_port

    def close(self): # Lukker connect
        self.con.close()

    def connect(self):  # Connect folger samme oppsett som LinRS test tool.
        con = serial.Serial(
            port=self.com_port, # COM-port defineres her
            baudrate=115200,  # Baudraten settes her
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        return con


def Hex(x, bytes=1):
    return hex(x)[2:].zfill(bytes * 2).upper()


def convert_mm_to_hex(mm):  # Gjør mm om til hex
    return Hex(int(mm * 10000), 4)  # resolution 0.1um


class Driver: # Kommandoer som sendes fra PC til driver og motsatt for forskjellige kommandoer.
    def __init__(self, connection, drive_id='01'):
        self.id = drive_id
        self.token = '02'
        self.connection = connection

    def telegramPstream(self, position):
        tel = '01' + self.id
        cont = '0902' + '0003'
        cont += convert_mm_to_hex(position)
        tel += Hex(len(cont)) + cont
        tel += '04'
        return tel

    def move_to_pos(self, x):
        self.connection.write(b16decode(self.telegramPstream(x)))

        if self.token == '02': # Veksler mellom 01 og 02, setter dette som token.
            self.token = '01'
        else:
            self.token = '02'

        dataString = "01" + self.id + "09020002" + self.token + "03" + convert_mm_to_hex(x) + "04"
        print('TX = ' + dataString + '(move to pos)')
        data = b16decode(dataString) # Dekoder datastringet med b16decode
        self.connection.write(data)  # Skriver data til driveren
        i = 30 # Intervall variabel lik 30.
        inputWord = ""
        while True:
            i -= 1
            inputByte = b16encode(self.connection.read())
            inputWord += inputByte
            if i < 0: #For å få programmet til å avslutte innen intervall lik 30.
                break
            if inputByte == '04': #Eller byte verdien 04 nås, avsluttes funksjonen.
                break
        return data

    def move_to_pos_VA_INT(self, x):

        if self.token == '02': # Veksler mellom 01 og 02, setter dette som token.
            self.token = '01'
        else:
            self.token = '02'

        dataString = "01" + self.id + "09020002" + self.token + "02" + self.encode(x) + "04"
        print 'TX = ' + dataString + '(move to pos)'
        data = base64.b16decode(dataString)
        self.connection.write(data)
        i = 30
        inputWord = ""
        while True:
            i -= 1
            inputByte = base64.b16encode(self.connection.read())
            inputWord += inputByte
            if i<0:
                break
            if inputByte == '04':
                break
        return data


    def decodebinstring(self, s):
        # gjor om binaerstreng til lesbar hex
        r = ''
        return r

    def move_home(self):
        data_string = "01" + self.id + "050200013F0804"
        print('TX = ' + data_string + ' (move home)')
        data = b16decode(data_string)
        self.connection.write(data)

        i = 30
        inputWord = ""
        while True:
            i -= 1
            inputByte = b16encode(self.connection.read())  # Writing Rx values one by one in byte.
            inputWord += inputByte
            if i < 0:  # Breaking when i<0.
                break
            if inputByte == "04":  # breaking matched 04.
                print('homing breaked and exited')
                break

    def stop_home(self):
        data_string = "01" + self.id + "050200013F0004"
        print('TX = ' + data_string + ' (stop home)')
        data = b16decode(data_string)
        self.connection.write(data)  # Skiver data til driver

    def read_status(self):
        inputWord = ""
        while con.in_waiting > 0:
            inputWord += b16encode(self.connection.read()) # Skriver Rx verdiene en etter en i byte (Fra driver til PC)
        if not inputWord[-2:] == "04":  # breaking matched 04.
            print('incomplete telegram')
        return inputWord

    def get_status(self):
        dataString = "01" + self.id + "05020001000004"
        data = b16decode(dataString) #Dekoder dataet ved bruk av b16decide
        self.connection.write(data) # Skiver data til driver
        return self.read_status()  # returnerer funksjonen

    def switch(self, bryter):
        if bryter == 'on':
            print("ON")
            dataString2 = "01" + self.id + "050200013F0004" # bryter til driver på
        else:
            print("OFF")
            dataString2 = "01" + self.id + "050200013E0004" # bryter av
        print('TX = ' + dataString2) # Bryter blitt enten slått på eller av avhengig av kom.
        self.connection.write(b16decode(dataString2)) # Skriver Tx verdien til driver
        time.sleep(0.1)
        self.read_status() # Leser status på driveren

    def read_pos(self): #finner egentlig posisjon fra driveren og gjoor den om til desimaler
        dataString = "01" + self.id + "0302010004" # Bruker request respons ex, se LinRs
        data = base64.b16decode(dataString)
        self.connection.write(data)  # skriv ut posisjon til driveren.
        i = 30

        inputWord_pos = ""
        while len(inputWord_pos) < 32:
            inputByte_pos = b16encode(self.connection.read()) # Leser verdiene fra driveren
            inputWord_pos += inputByte_pos # Legger til en og en byte
            #print('RX = ' + inputByte)
        print('vv ' + inputWord_pos)
        if inputWord_pos < 29:  # hvis outputverdiene fra driveren er mindre enn 29, feilmelding
            print('Feilmelding')
        else:
            y1 = inputWord_pos[22]
            y2 = inputWord_pos[23]
            y3 = inputWord_pos[24]
            y4 = inputWord_pos[25]
            y5 = inputWord_pos[26]
            y6 = inputWord_pos[27]
            y7 = inputWord_pos[28]
            y8 = inputWord_pos[29]
            y = [y8, y7, y5, y6, y3, y4, y1, y2]  # endrer rekkefoolgen til hex.
            str1 = ''.join(y)
            hex = int(str1, 16)  # finner desimaltall
            dec = hex / float(10000)
            if dec > 429496:  # feil med 0.
                print(0)
            else:
                print(dec)



if __name__ == '__main__':
    #Test code for module

    con = Kobling('COM7').connect()
    lin = Driver(con, '01')

    lin.switch('off')
    lin.switch('on')

    lin.move_home()
    time.sleep(8)
    lin.stop_home()
    time.sleep(8)
    tick = time.clock()
    for i in range(0, 5, 1):
        tick += .02
        lin.move_to_pos(i)
        lin.read_pos()
        while time.clock() < tick:
            pass
    con.close()

