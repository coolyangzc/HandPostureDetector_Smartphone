import os.path

from data_format import PIXELS
from data_format import data_to_edge

dir = "..\Sentons_Data"

category = [[] for i in range(2)]
category[0] = ['V_L', 'V_L_F', 'V_L_A']
category[1] = ['V_R', 'V_R_F', 'V_R_A']
#category[2] = ['V_D', 'V_D_F', 'V_D_A']

duplicate_removal = False

def analyse(fd, catg, outfd, mission, username):
    lines = fd.readlines()
    last_data = []
    for line in lines[2:]:
        data = line[:-1].split(' ')[2:]
        if duplicate_removal and cmp(data, last_data) == 0:
            continue
        area = [0, 0]
        forces = [0, 0]
        count = [0, 0]
        n = int(data[0])
        p = 1
        for touch in range(n):
            bar = int(data[p])
            force = int(data[p + 2])
            pos0 = float(data[p + 4])
            pos1 = float(data[p + 5])
            count[bar] += 1
            forces[bar] += force
            area[bar] += force * (pos1 - pos0)
            p += 6
        outfd.write(username + ',' + mission + ',')
        sum_area = area[0] + area[1]
        if sum_area == 0:
            outfd.write('0,0,0,0,')
        else:
            outfd.write(str(sum_area) + ',' +
                        str(count[0] / float(count[0] + count[1])) + ',' +
                        str(forces[0] / float(forces[0] + forces[1])) + ',' +
                        str(area[0] / sum_area) + ',')
        outfd.write(str(catg) + '\n')
        last_data = data

output_filename = '..\Sentons_Result\data_analyse.txt'
outfd = open(output_filename, 'w')
outfd.write('User,Mission,TotalArea*Force,RightPortion(Count),RightPortion(Force),RightPortion(Area*Force),Category(L0/R1)\n')
for parent, dirnames, filenames in os.walk(dir):
    for filename in filenames:
        fd = file(os.path.join(parent, filename))
        tag = fd.readline()
        tag = tag[:-1]
        for i in range(len(category)):
            if tag in category[i]:
                analyse(fd, i, outfd, tag, parent.split('\\')[-1])
                print 'Reading ' + os.path.join(parent, filename)
                break
outfd.close()