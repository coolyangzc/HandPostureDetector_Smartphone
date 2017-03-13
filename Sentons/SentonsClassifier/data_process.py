import os
import os.path

dir = "..\Sentons_Data"

category = [[] for i in range(2)]
category[0] = ['V_L', 'V_L_F']
category[1] = ['V_R', 'V_R_F']

EDGE_MM = 116
PIXELS = 116

output_filename = '..\Sentons_Data\data.txt'
outfd = open(output_filename, 'w')

def process(fd, catg):
    lines = fd.readlines()    
    for line in lines[2:]:
        data = line[:-1].split(' ')
        n = int(data[2])
        if (n == 0):
            continue
        p = 3
        edge = [[0 for i in range(PIXELS)] for i in range(2)]
        for i in range(n):
            bar = int(data[p])
            force = int(data[p+2])
            pos0 = float(data[p+4])
            pos1 = float(data[p+5])
            pos0 = int(round(pos0 / EDGE_MM * (PIXELS - 1)))
            pos1 = int(round(pos1 / EDGE_MM * (PIXELS - 1)))
            for i in range(pos0, pos1 + 1):
                edge[bar][i] += force
            for i in range(2):
                for j in range(PIXELS):
                    outfd.write(str(edge[i][j]) + ' ')
            outfd.write(str(catg) + '\n')
            

outfd.write(str(PIXELS) + '\n') 
for parent, dirnames, filenames in os.walk(dir):
    for filename in filenames:
        print 'Reading ' + os.path.join(parent, filename)
        fd = file(os.path.join(parent, filename))
        tag = fd.readline()
        tag = tag[:-1]
        for i in range(len(category)):
            if (tag in category[i]):
                process(fd, i)
                break
outfd.close()
