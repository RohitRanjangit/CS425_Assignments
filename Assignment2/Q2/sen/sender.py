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


class Sender:

    def __init__(self, window_size, timeout):
        self.w = window_size                     #sender's window size
        self.t = timeout
        self.filename = "FileToTransfer.txt"  #file to be transferred
        self.cur_seq = 0                      #current sequence
        self.active_spaces = self.w           #free space in window
        self.window = window_size * [None]       #buffer
        self.soc = socket.socket() 
        self.last_sent_seqnum = -1            #last sent sequence number
        self.last_ack_seqnum = -1             #last acknowledged sequence number
        
    def canAdd(self):  # check if a packet can be added to the send window
        if self.active_spaces == 0:
            return False
        else:
            return True


    def addAndSend(self, pack):  # add a packet to the send window
        self.last_sent_seqnum = self.cur_seq
        self.cur_seq += 1
        self.window[self.w - self.active_spaces] = pack
        self.active_spaces -= 1
        time.sleep(1.5)
        data=pack
        conn.send(data.encode('utf-8'))
        time.sleep(2)
        print("Sending packet: ", pack.split('/////'))
    

    def resend(self):  # function to resend packet if lost
        print('resending packets in the window....')
        print('self.active_spaces='+str(self.active_spaces))
        print('self.window='+str(self.window))
        ##
        ##          
        ## send the packets in the self.window one by one. Add probability=random.randint(0,100)
        ##
        ##print the packet sent (after sending)

        #resend all packets in windows which are not None 
        for packet in self.window:

            if packet:

                packet = packet.split('/////')
                #print('debug64', packet)
                packet[-1] = str(random.randint(0,100))
                #print('debug66', packet)
                data = '/////'.join(packet)
                time.sleep(1.5)
                conn.send(data.encode('utf-8'))
                time.sleep(2)
                print("resending packet: ", packet)
            
    def separateChunks(self, message):
        splitted=message.split('/////')
        received=[]
        NumberOfItems=int((len(splitted)-1)/2)
        print(NumberOfItems)
        j=1
        k=2
        received.append('')
        if NumberOfItems!=1:
            print('separating packet collected from pipe')
            for i in range(0,NumberOfItems):
                if i==0:
                    x=splitted[0]
                else:
                    received.append('')
                y=splitted[j]
                j=j+2
                mergedTexted=splitted[k]
                k=k+2
                z=mergedTexted[0:3]
                received[i]=x+'/////'+y+'/////'+z
                x= mergedTexted[3:len(mergedTexted)]
                print(received[i])
        else:
            received[0]=message
        print(received)
        return received
                

    def makePack(self, num, pack):  # Create a packet

        probability = random.randint(0,100) # probability_that_the_packet_will_reach 
        ## we use this probability to check the correctness of the modules assuming the data is not received by the receiver if probability<70 
        ## prepare the packet in format "checksum/////sequence_number/////Length_of_packet/////data_in_packet/////probability"

        assert isinstance(pack, str), "pack must in str format in makePack"
        #print('debug107', str(check_sum(pack.encode('utf-8'))))
        packet = str(check_sum(pack.encode('utf-8'))) + '/////' + str(num) + '/////' + str(len(pack)) + '/////' + str(pack) + '/////' + str(probability)

        return packet
    

    def divide(self, data, num):  # create list of chunks from datas
        lis = []
        while data:
            lis.append(data[:num])
            data = data[num:]
        return lis

    
   
    def acc_Acks(self):  # check if all the sent packets have been ACKed
        print('checking if all the sent packets have been ACKed')
        print('receiving the packets....')
        try:
            data = conn.recv(1024) #receive message from receiver
            packet=data.decode('utf-8')
            received=self.separateChunks(packet)
        except: #if the message does not arrive within time bound print on console "'Connection lost due to timeout!'" and return 0
            print('Connection lost due to timeout!') 
            return 0
        
        """
        ## Testcase for points (3) and (4) in section 2.3:
        
        received_packet='c81e728d9d4c2f636f067f89cc14862c/////2/////NAK'
        self.window=["f861c77c48e93c3221f61d/////0/////10/////b'Go-Back-N '/////57",\
                     "fdbeff054b0c917df19343c/////1/////10/////b'ARQ is a s'/////30",\
                     "b6e2213c855aa95dfd97732/////2/////10/////b'pecific in'/////62", \
                     "dc7fd4698c43bea0469e76/////3/////7/////b'stance.'/////52"]
        self.w = 4
        self.active_spaces=0
        self.last_ack_seqnum = 0
        """
        ##        
        ## if message='NAK' return 0
        ##----else: print "Received Ack number:" ACK_number, update the variables and slide the window accordingly.
        ## print the variables before and after this function as explained in Point(2) and (3) in section 2.3

        #print('debug152', received)

        #Assume window size is 5

        #The possible values of 'recieved' are :[ack, ack, ack, nak] , [nak], [ack, ack, ack, ack,ack]
        #for the first value, this function will slide windows three times
        #for the second, it's just return False
        #Third case, the whole will [None, None, None, None, None]


        last_ack = received[-1].split('/////')  # retrievce last ack

        print("The received packet is: ", received[-1])

        retval = True #return value

        if last_ack[-1] == 'NAK': #last is nak, remove last nak instance from 'received'
            retval = False
            received = received[:-1]
        
        if not received:   #third case
            return retval

        assertFlag = True
        for ack_msg in received:
            if ack_msg.split('/////')[-1] == 'NAK':
                assertFlag = False
                break
        
        assert assertFlag, "NAK can't be in between in acks sent by receiver, it must be at last"
        
        #print before update
        
        print("self.last_ack_seqnum=", self.last_ack_seqnum)
        print("self.active_space=", self.active_spaces)
        print("self.w=", self.w)
        print("self.window=", self.window)
        
        for _ in range(int(received[-1].split('/////')[1]) - self.last_ack_seqnum):
            self.window.pop(0)
            self.window.append(None)
            self.active_spaces += 1
        
        #print('debug195', received[-1].split('/////'))
        #update ack seqnum to last received ack seq num
        self.last_ack_seqnum = int(received[-1].split('/////')[1])

        
        print("self.last_ack_seqnum=", self.last_ack_seqnum)
        print("self.active_space=", self.active_spaces)
        print("self.w=", self.w)
        print("self.window=", self.window)
        
        return retval



    def SendMessage(self, pack_list):  # send the messages till all packets are sent
        ##
        ## pack_list is the list of data chunks. This function will end after the complete list is sent.
        ## using function makePack() create the packets
        ## print the packet on console
        ## using the fuction "addAndSend(pack)"" add the packet to the window and send it.
        ## 
        ## if receiver sent 'NAK' or receiver could not send ACK within the defined time then:
        ##   print('need to resend the packets available in the window.')
        ##   self.resend()  # resend the packets in the window.
        

        while self.cur_seq < len(pack_list):
            #Add packet to the window while there is any space left
            while self.cur_seq < len(pack_list) and self.canAdd():
                #print('debug224', self.window)
                packed_msg = self.makePack(self.cur_seq, pack_list[self.cur_seq])
                self.addAndSend(packed_msg)
            #check ack received
            if not self.acc_Acks():
                self.resend()
        
        #sent any left packets
        while any(self.window):
            if not self.acc_Acks():
                self.resend()
         
            

        print("END")
        time.sleep(1)
        data="$$$$$$$"
        conn.send(data.encode('utf-8'))
        time.sleep(1)

    def SendPacketsFromFile(self):  # to send packets from the file
        try:
            fil = open(self.filename, 'r')
            data = fil.read()
            pack_list = self.divide(data, 25)
            fil.close()
        except IOError:
            print("No such file exists")
        l=len(pack_list)
        self.SendMessage(pack_list)


win = input("Enter window size: ")   
tim = input("Enter the timeout: ")

server=Sender(int(win), float(tim))

server.soc.bind((host, port))
server.soc.listen(5)
conn, addr=server.soc.accept()
data = conn.recv(1024)
print("received connection")
response=str(win) + "/////" + str(tim) + "/////" + "FileToTransfer.txt"
conn.send(response.encode('utf-8'))
conn.close()

server.soc.settimeout(5)
conn, addr = server.soc.accept()
data = conn.recv(1024)
server.SendPacketsFromFile()
conn.close()