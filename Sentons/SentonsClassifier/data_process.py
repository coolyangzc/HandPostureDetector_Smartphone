import os
import os.path

from data_format import PIXELS
from data_format import data_to_edge

dir = "..\Sentons_Data"

category = [[] for i in range(2)]
category[0] = ['V_L', 'V_L_F', 'V_L_A']
category[1] = ['V_R', 'V_R_F', 'V_R_A']
#category[2] = ['V_D', 'V_D_F', 'V_D_A']


def process(fd, catg, outfd):
    lines = fd.readlines()    
    for line in lines[2:]:
        data = line[:-1].split(' ')[2:]
        n, edge = data_to_edge(data)
        if n <= 0:
            continue
        for i in range(len(edge)):
            if edge[i] == 0:
                outfd.write('0 ')
            else:
                outfd.write(str(round(edge[i], 2)) + ' ')
        outfd.write(str(catg) + '\n')

output_filename = '..\Sentons_Data\data.txt'
outfd = open(output_filename, 'w')
outfd.write(str(PIXELS) + '\n') 
for parent, dirnames, filenames in os.walk(dir):
    for filename in filenames:
        if filename == 'data.txt':
            continue
        print 'Reading ' + os.path.join(parent, filename)
        fd = file(os.path.join(parent, filename))
        tag = fd.readline()
        tag = tag[:-1]
        for i in range(len(category)):
            if tag in category[i]:
                process(fd, i, outfd)
                break
outfd.close()