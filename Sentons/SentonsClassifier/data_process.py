import os
import os.path

dir = "..\Sentons_Data"

category = [[] for i in range(2)]
category[0] = ['V_L_F'] #['V_L', 'V_L_F']
category[1] = ['V_R_F'] #['V_R', 'V_R_F']

EDGE_MM = 116
PIXELS = 116

def data_to_edge(data):
    n = int(data[0])
    edge = [0 for i in range(PIXELS) * 2]
    p = 1
    for i in range(n):
        bar = int(data[p])
        force = int(data[p+2])
        pos0 = float(data[p+4])
        pos1 = float(data[p+5])
        pos0 = int(round(pos0 / EDGE_MM * (PIXELS - 1)))
        pos1 = int(round(pos1 / EDGE_MM * (PIXELS - 1)))
        for i in range(pos0, pos1 + 1):
            edge[bar * PIXELS + i] += force
        p += 6
    return n, edge

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

def main():
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
