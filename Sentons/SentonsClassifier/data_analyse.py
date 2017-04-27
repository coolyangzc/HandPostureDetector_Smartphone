import os.path

dir = "..\Sentons_Data"


#bar: L = 1, R = 0
#pos: Up = 116, Down = 0

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
        gravity = [0, 0]
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
            gravity[bar] += force * (pos1 - pos0) * (pos0 + pos1) / 2
            p += 6
        for bar in range(2):
            if area[bar] != 0:
                gravity[bar] /= area[bar]
        outfd.write(username + ',' + mission + ',')
        sum_area = area[0] + area[1]
        if sum_area == 0:
            for i in range(12):
                outfd.write('0,')
        else:
            outfd.write(str(sum_area) + ',' +
                        str(count[1]) + ',' + str(count[0]) + ',' + str(count[1])+'_'+str(count[0]) + ',' +
                        str(count[0] / float(count[0] + count[1])) + ',' +
                        str(forces[0] / float(forces[0] + forces[1])) + ',' +
                        str(area[1]) + ',' + str(area[0]) + ',' + str(area[0] / sum_area) + ',' +
                        str(gravity[1]) + ',' + str(gravity[0]) + ',' + str(gravity[1] - gravity[0]) + ',')
        outfd.write('L\n' if catg == 0 else 'R\n')
        last_data = data

output_filename = '..\Sentons_Result\data_analyse.txt'
outfd = open(output_filename, 'w')
outfd.write('User,Mission,Total(Area*Force),')
outfd.write('L(Count),R(Count),L_R(Count),RightPortion(Count),')
outfd.write('RightPortion(Force),')
outfd.write('L(Area*Force),R(Area*Force),RightPortion(Area*Force),')
outfd.write('L(Gravity),R(Gravity),L-R(Gravity),')
outfd.write('Category(L/R)\n')
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