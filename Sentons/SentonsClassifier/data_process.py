import os
import os.path

from data_format import PIXELS
from data_format import data_to_edge

dir = "..\Sentons_Data"

category = [[] for i in range(2)]
category[0] = ['V_L', 'V_L_F']
category[1] = ['V_R', 'V_R_F']

def process(fd, catg, outfd):
    lines = fd.readlines()    
    for line in lines[2:]:
        data = line[:-1].split(' ')[2:]
        n, edge = data_to_edge(data)
        if (n <= 0):
            continue
        for i in range(len(edge)):
            outfd.write(str(edge[i]) + ' ')
        outfd.write(str(catg) + '\n')

output_filename = '..\Sentons_Data\data.txt'
outfd = open(output_filename, 'w')
outfd.write(str(PIXELS) + '\n') 
for parent, dirnames, filenames in os.walk(dir):
    for filename in filenames:
        if (filename == 'data.txt'):
            continue
        print 'Reading ' + os.path.join(parent, filename)
        fd = file(os.path.join(parent, filename))
        tag = fd.readline()
        tag = tag[:-1]
        for i in range(len(category)):
            if (tag in category[i]):
                process(fd, i, outfd)
                break
outfd.close()