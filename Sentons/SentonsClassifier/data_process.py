import os.path

from data_format import PIXELS
from data_format import data_to_edge

dir = "..\Sentons_Data"

category = [[] for i in range(2)]
category[0] = ['V_L', 'V_L_F', 'V_L_A']
category[1] = ['V_R', 'V_R_F', 'V_R_A']
#category[2] = ['V_D', 'V_D_F', 'V_D_A']

duplicate_removal = False

def process(fd, catg, outfd, user_id):
    lines = fd.readlines()
    last_data = []
    for line in lines[2:]:
        data = line[:-1].split(' ')[2:]
        if duplicate_removal and cmp(data, last_data) == 0:
            continue
        n, edge = data_to_edge(data)
        if n <= 0:
            continue
        outfd.write(str(user_id) + ' ')
        for i in range(len(edge)):
            if edge[i] == 0:
                outfd.write('0 ')
            else:
                outfd.write(str(round(edge[i], 2)) + ' ')
        outfd.write(str(catg) + '\n')
        last_data = data

output_filename = '..\Sentons_Result\data_nonunique.txt'
outfd = open(output_filename, 'w')
outfd.write(str(PIXELS) + '\n')
last_parent = ''
user_id = -1
for parent, dirnames, filenames in os.walk(dir):
    for filename in filenames:
        if filename == 'data.txt':
            continue
        print 'Reading ' + os.path.join(parent, filename)
        if parent != last_parent:
            user_id += 1
        fd = file(os.path.join(parent, filename))
        tag = fd.readline()
        tag = tag[:-1]
        for i in range(len(category)):
            if tag in category[i]:
                process(fd, i, outfd, user_id)
                break
        last_parent = parent
outfd.close()