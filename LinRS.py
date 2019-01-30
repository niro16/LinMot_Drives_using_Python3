from __future__ import print_function
import serial
from base64 import b16encode, b16decode
import time


class Kobling: # Communication between LinMot servo drive and computer. This class is about to get all components used to communicate with each other.
    def __init__(self, com_port):
        self.com_port = com_port

    def close(self): # Close connect
        self.con.close()

    def connect(self):
        con = serial.Serial(
            port=self.com_port, # COM-port
            baudrate=115200,  # Baudrate
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        return con


def Hex(x, bytes=1):
    return hex(x)[2:].zfill(bytes * 2).upper()


def convert_mm_to_hex(mm):  # Converts from mm to hex
    return Hex(int(mm * 10000), 4)  # resolution 0.1um


class Driver: # Sends different motion commands from computer to servo drive, and vice versa. This class is all about driving the LinMot drive
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
            if i < 0: # To get the program to quit after an 30 iterations
                break
            if inputByte == '04': # Or quit when byte value '04' is reached
                break
        return data

    def move_to_pos_VA_INT(self, x):

        if self.token == '02': # Alternating between 01 og 02, labelling this as token.
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
        # Converting binary string to readable hex
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
        self.connection.write(data)  # Writing data to the drive

    def read_status(self):
        inputWord = ""
        while con.in_waiting > 0:
            inputWord += b16encode(self.connection.read()) # Writes Rx values one by one in byte. (From the servo drive to a PC)
        if not inputWord[-2:] == "04":  # breaking matched 04.
            print('incomplete telegram')
        return inputWord

    def get_status(self):
        dataString = "01" + self.id + "05020001000004"
        data = b16decode(dataString) #Decoding the data using b16decode
        self.connection.write(data)
        return self.read_status()

    def switch(self, bryter):
        if bryter == 'on':
            print("ON")
            dataString2 = "01" + self.id + "050200013F0004" # Switching on the servo drive
        else:
            print("OFF")
            dataString2 = "01" + self.id + "050200013E0004" # bryter av
        print('TX = ' + dataString2)
        self.connection.write(b16decode(dataString2)) # Writing Tx values to the servo drive
        time.sleep(0.1)
        self.read_status() # reading status on the servo drive

    def read_pos(self): # Reading the actual position of the linMot drive
        dataString = "01" + self.id + "0302010004" # Requesting the position of the linMot
        data = base64.b16decode(dataString)
        self.connection.write(data)
        i = 30

        inputWord_pos = ""
        while len(inputWord_pos) < 32:
            inputByte_pos = b16encode(self.connection.read())
            inputWord_pos += inputByte_pos
            #print('RX = ' + inputByte)
        print('vv ' + inputWord_pos)
        if inputWord_pos < 29:  # If output value is less than 29 --> "Error"
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
            y = [y8, y7, y5, y6, y3, y4, y1, y2]  # Change the order of the hex values.
            str1 = ''.join(y)
            hex = int(str1, 16)
            dec = hex / float(10000)
            if dec > 429496:
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

