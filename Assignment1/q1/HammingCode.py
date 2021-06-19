#!/usr/bin/env python
# coding: utf-8

# In[100]:


from PIL import Image
import sys
from numpy import array
import numpy 


# In[101]:


def LeftShiftRotate(oldstate): 
    leftbit = oldstate[0]
    for i in range(0,14):
        oldstate[i] = oldstate[i+1]
    oldstate[14] = leftbit
    newstate = oldstate
    return newstate


# In[102]:


def string_converter(bitstring):
    output_string = ""
    output_string = bitstring[2]+bitstring[4]+bitstring[5]+bitstring[6]+bitstring[8]+bitstring[9]+bitstring[10]+bitstring[11]+bitstring[12]+bitstring[13]+bitstring[14]
    return output_string


# In[167]:


def hamming_decode(bitstring):
#     chars_seq = bitstring
    bit_seq = []
    decoded_rem = []
    for i in bitstring:
        bit_seq = bit_seq + [int(i)]
        
    bit_seq_arr = array(bit_seq)
    bit_seq_arr = numpy.reshape(bit_seq_arr,(15,1))
    Res = numpy.dot(H_prime,bit_seq_arr)
    Res = numpy.mod(Res,2)
#     print(Res)
    Res = numpy.reshape(Res,(1,4))
    result = Res.tolist()
    result = result[0]
#     print(result)
    return result
  
#     for ii in range(4):
#         res = 0
#         for k in range(15):
#             res = res ^ (bit_seq[k] * H[ii][k])
#         decoded_rem = decoded_rem + [res]
#     return decoded_rem


# In[168]:


def hamming_encode(bitstring):
    chars_seq = bitstring
    bit_seq = []
    encoded_seq = 15*[0]
    for i in chars_seq:
        bit_seq = bit_seq + [int(i)] 
#     print(bit_seq)
        
#     for i in range(15):
#         res = 0
#         for k in range(11):
#             res = res ^ (bit_seq[k] * G[k][i])
#         encoded_seq = encoded_seq + [res]
        
    encoded_seq[0] = bit_seq[0]^bit_seq[1]^bit_seq[3]^bit_seq[4]^bit_seq[6]^bit_seq[8]^bit_seq[10]
    encoded_seq[1] = bit_seq[0]^bit_seq[2]^bit_seq[3]^bit_seq[5]^bit_seq[6]^bit_seq[9]^bit_seq[10]
    encoded_seq[2] = bit_seq[0]
    encoded_seq[3] = bit_seq[1]^bit_seq[2]^bit_seq[3]^bit_seq[7]^bit_seq[8]^bit_seq[9]^bit_seq[10]
    encoded_seq[4] = bit_seq[1]
    encoded_seq[5] = bit_seq[2]
    encoded_seq[6] = bit_seq[3]
    encoded_seq[7] = bit_seq[4]^bit_seq[5]^bit_seq[6]^bit_seq[7]^bit_seq[8]^bit_seq[9]^bit_seq[10]
    encoded_seq[8] = bit_seq[4]
    encoded_seq[9] = bit_seq[5]
    encoded_seq[10] = bit_seq[6]
    encoded_seq[11] = bit_seq[7]
    encoded_seq[12] = bit_seq[8]
    encoded_seq[13] = bit_seq[9]
    encoded_seq[14] = bit_seq[10]
    encoded_string = ""
#     print(encoded_seq)
    for i in encoded_seq:
        encoded_string = encoded_string + str(i)
#     print(encoded_string)
    return encoded_string




# In[172]:


def ReadImage():
    
    image_name = sys.argv[1]       
    image_ = Image.open(image_name)
    flip_bits =  list(map(int,list(sys.argv[2].split(','))))
    pixel_ = image_.load()
    width, height = image_.size
    sender = open("sender.txt", 'w')
    receiver = open("receiver.txt", 'w')

    for y in range (0, height):
        for x in range (0, width):
            num_r = str(pixel_[x,y][0])
            num_g = str(pixel_[x,y][1])
            num_b = str(pixel_[x,y][2])

            r = '000' + f'{pixel_[x,y][0]:08b}'
#             print(r)
            g = '000' + f'{pixel_[x,y][1]:08b}'
#             print(g)
            b = '000' + f'{pixel_[x,y][2]:08b}'
#             print(b)
      
            encoded_r = hamming_encode(r)
            encoded_g = hamming_encode(g)
            encoded_b = hamming_encode(b)

            output = ""
            output = output + "{" + num_r + "," + num_g + "," + num_b + "}" + " " + "{" + encoded_r + "," + encoded_g + "," + encoded_b + "}"
            sender.write(output + '\n')
            # print(output, file=open("sender.txt", "a"))
            # print(output)


      #part1 ends here

            encoded_r_list = []
            for i in encoded_r:
                encoded_r_list = encoded_r_list + [int(i)]
            encoded_g_list = []
            for i in encoded_g:
                encoded_g_list = encoded_g_list + [int(i)]
            encoded_b_list = []
            for i in encoded_b:
                encoded_b_list = encoded_b_list + [int(i)]

            for i in range(15):
                encoded_r_list[i] = encoded_r_list[i] ^ flip_bits[i]
                encoded_g_list[i] = encoded_g_list[i] ^ flip_bits[i]
                encoded_b_list[i] = encoded_b_list[i] ^ flip_bits[i]

            to_be_decoded_r = ""
            for i in encoded_r_list:
                to_be_decoded_r = to_be_decoded_r + str(i)
            # print(encoded_r)
            # print(to_be_decoded_r)
            to_be_decoded_g = ""
            for i in encoded_g_list:
                to_be_decoded_g = to_be_decoded_g + str(i)
            to_be_decoded_b = ""
            for i in encoded_b_list:
                to_be_decoded_b = to_be_decoded_b + str(i)

            decoded_r_rem = hamming_decode(to_be_decoded_r)
            # print(decoded_r_rem)
            decoded_g_rem = hamming_decode(to_be_decoded_g)
            decoded_b_rem = hamming_decode(to_be_decoded_b)

            rem = [0,0,0,0]
            codes = ['p1', 'p2', 'd3', 'p4', 'd5', 'd6', 'd7', 'p8', 'd9', 'd10', 'd11', 'd12', 'd13', 'd14', 'd15']
            output = ""
            
            
            if(decoded_r_rem == rem):
                guess = string_converter(to_be_decoded_r)
                output = output + "Valid " + guess + " "
            else:
                error_col = 0
                for i in range(15):
                    temp = 0
                    for j in range(4):
                        if(decoded_r_rem[j] == H[j][i]):
                            temp = temp+1
                    if(temp == 4):
                        error_col = i
                        break
                        
                str1_list = list(to_be_decoded_r)
                if(str1_list[error_col] == '0'):
                    str1_list[error_col] = '1'
                else:
                    str1_list[error_col] = '0'
                str1 = ""
                str1 = str1.join(str1_list)
                guess = string_converter(str1)
                output = output + codes[error_col] + " " + guess + " "
                
            
            if(decoded_g_rem == rem):
                guess = string_converter(to_be_decoded_g)
                output = output + "Valid " + guess + " "
            else:
                error_col = 0
                for i in range(15):
                    temp = 0
                    for j in range(4):
                        if(decoded_g_rem[j] == H[j][i]):
                            temp = temp+1
                    if(temp == 4):
                        error_col = i
                        break
                        
                str1_list = list(to_be_decoded_g)
                if(str1_list[error_col] == '0'):
                    str1_list[error_col] = '1'
                else:
                    str1_list[error_col] = '0'
                str1 = ""
                str1 = str1.join(str1_list)
                guess = string_converter(str1)
                output = output + codes[error_col] + " " + guess + " "
                
                
                
            if(decoded_b_rem == rem):
                guess = string_converter(to_be_decoded_b)
                output = output + "Valid " + guess + " "
            else:
                error_col = 0
                for i in range(15):
                    temp = 0
                    for j in range(4):
                        if(decoded_b_rem[j] == H[j][i]):
                            temp = temp+1
                    if(temp == 4):
                        error_col = i
                        break
                        
                str1_list = list(to_be_decoded_b)
                if(str1_list[error_col] == '0'):
                    str1_list[error_col] = '1'
                else:
                    str1_list[error_col] = '0'
                str1 = ""
                str1 = str1.join(str1_list)
                guess = string_converter(str1)
                output = output + codes[error_col] + " " + guess + " "

      

            # print(output, file=open("receiver.txt", "a"))
            receiver.write(output+'\n')
        flip_bits = LeftShiftRotate(flip_bits)
            # print(output)
        #     break
        # break
      
            


# In[173]:


G =                [ [ 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0],
                     [ 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                     [ 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                     [ 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
                     [ 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
                     [ 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
                     [ 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1],
                     [ 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1],
                     [ 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1],
                     [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1],
                     [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1] ]


H = [[1,1,0,1,1,0,1,0,1,0,1,1,0,0,0],
     [1,0,1,1,0,1,1,0,0,1,1,0,1,0,0],
     [0,1,1,1,0,0,0,1,1,1,1,0,0,1,0],
     [0,0,0,0,1,1,1,1,1,1,1,0,0,0,1]]

H_prime = array(H)


# In[174]:


ReadImage()


# In[175]:


a = [1,1,0,0,0,0,0,1,0,0,0,0,1,0,0]
aa = array(a)
aa = numpy.reshape(aa,(15*1))
r = H_prime.dot(aa)


# In[166]:


r


# In[ ]:




