import socket
import time
import os
import hashlib
import random

host = ""
port = 9999


def check_sum(data):
    hash_md5 = hashlib.md5()
    hash_md5.update(data)
    return hash_md5.hexdigest()


class Receiver:

    def __init__(self,win_size, timeout, filename):
        
        self.w = win_size                #sender's window size
        self.completeData = ''           #complete data collected by the transfer from sender, is written to the file at the end of the transfer
        self.t = timeout    
        self.base = 0
        self.expec_seqnum = 0            #expected sequence number
        self.last_ack_sent = -1          #last acknowledged sequence
        self.soc = socket.socket()  
        self.window = [None] * self.w    #buffer
        self.active_win_packets = self.w #space in buffer
        self.fileclone = filename        #file to write the data received from the sender
        self.logfile = ''
        self.filepointer = 0


    def canAdd(self):  # check if a packet can be added to the buffer
        if self.active_win_packets == 0:
            return False
        else:
            return True

    def createResponse(self, seq_num, typ):
        mess_check_sum = check_sum(str(seq_num).encode('utf-8'))
        return str(mess_check_sum) + "/////" + str(seq_num) + "/////" + typ

    def sendAcks(self, packet, counter):
        if counter == -1:
            data=packet.encode('utf-8')
            self.soc.send(data)
            time.sleep(1)
            print("Sending ack: ", str(packet.split('/////')[1]) + "NAK\n")
            return
        self.last_ack_sent = int(packet.split("/////")[1]) + counter
        time.sleep(1.7)
        data=packet.encode('utf-8')
        self.soc.send(data)
        time.sleep(1)
        print("Sending ack: ", str(packet.split('/////')[1]) + "ACK\n")

    def remove(self, poin):
        self.window[self.window.index(poin)] = None
        self.active_win_packets += 1

    def add(self, packet):
        pack = packet.split('/////')[3]
        seqnum = int(packet.split('/////')[1])
        if self.window[seqnum % self.w] == None:
            if seqnum == self.expec_seqnum:
                self.active_win_packets -= 1
                self.window[seqnum % self.w] = packet
            elif seqnum > self.expec_seqnum:
                self.active_win_packets -= 1
                self.window[seqnum % self.w] = packet

        else:
            print("In buffer!", packet.split('/////')[1])

    def appData(self):
        data=self.window[self.filepointer].split('/////')[3]
        self.completeData += data
        self.filepointer += 1
        self.window[self.window.index(self.window[self.filepointer - 1])] = None #remove from the buffer
        self.active_win_packets += 1
        if self.filepointer >= self.w:
            self.filepointer = 0

    def rMessage(self):
        while True:
            data = self.soc.recv(1024)
            coun = 0
            pack=data.decode('utf-8')
            print(pack.split('/////'),self.expec_seqnum)
            if pack == '$$$$$$$':
                f = open(self.fileclone, 'wb')
                data=self.completeData
                f.write(data.encode('utf-8'))
                f.close()
                break
            elif int(pack.split('/////')[1]) == self.expec_seqnum:
                nex = 0
                if self.canAdd():
                    try:
                        k = int(pack.split("/////")[4])
                    except:
                        nex = 1
                    if not nex:
                        if int(pack.split("/////")[4]) >= 50:
                            self.add(pack)
                            packet = self.createResponse(self.expec_seqnum + coun, "ACK")                            
                            while self.window[(int(pack.split('/////')[1]) + coun) % self.w] != None:
                                self.appData()
                                packet = self.createResponse(self.expec_seqnum + coun, "ACK")
                                coun = coun + 1
                        else:
                            packet = self.createResponse(self.expec_seqnum + coun, "NAK")
                    else:
                        packet = self.createResponse(self.expec_seqnum + coun, "NAK")
                   
                self.sendAcks(packet, coun - 1)
                time.sleep(1)
                self.expec_seqnum = self.expec_seqnum + coun
            else:
                if self.canAdd():
                    self.add(pack)

    def receive(self):
        self.rMessage()

s = socket.socket()
s.connect((host, port))
s.send("Hello Server".encode('utf-8'))
mess = s.recv(1024)
data=mess.decode('utf-8')
args = data.split("/////")
s.close()
client = Receiver(int(args[0]), float(args[1]), args[2])
print("received arguments")
client.soc.connect((host, port))
data="Hello server"
client.soc.send(data.encode('utf-8'))
client.receive()
client.soc.close()
