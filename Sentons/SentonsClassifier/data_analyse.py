import os.path

dir = "..\Sentons_Data"


# bar: L = 1, R = 0
# pos: Up = 116, Down = 0

category = [[] for i in range(2)]
category[0] = ['V_L', 'V_L_F', 'V_L_A']
category[1] = ['V_R', 'V_R_F', 'V_R_A']
# category[2] = ['V_D', 'V_D_F', 'V_D_A']
bar_catg = ['L', 'R']
L = 0
R = 1

duplicate_removal = False
zero_removal = True


def analyse(fd, catg, outfd, mission, username):
    lines = fd.readlines()
    last_data = []
    for line in lines[2:]:
        data = line[:-1].split(' ')[2:]
        if duplicate_removal and cmp(data, last_data) == 0:
            continue
        n = int(data[0])
        area = [0, 0]
        forces = [0, 0]
        count = [0, 0]
        gravity = [0, 0]
        highest = [0, 0]
        longest = [0, 0]
        p = 1
        for touch in range(n):
            bar = int(data[p]) ^ 1
            force = int(data[p + 2])
            pos0 = float(data[p + 4])
            pos1 = float(data[p + 5])
            count[bar] += 1
            forces[bar] += force
            area[bar] += force * (pos1 - pos0)
            gravity[bar] += force * (pos1 - pos0) * (pos0 + pos1) / 2
            highest[bar] = max(highest[bar], pos1)
            longest[bar] = max(longest[bar], pos1 - pos0)
            p += 6
        sum_area = area[0] + area[1]
        if zero_removal and sum_area == 0:
            continue
        for bar in range(2):
            if area[bar] != 0:
                gravity[bar] /= area[bar]
        outfd.write(username + ',' + mission + ',')

        if sum_area == 0:
            if zero_removal:
                continue
            for i in range(18):
                outfd.write('0,')
        else:
            outfd.write(str(sum_area) + ',')
            for i in range(2):
                outfd.write(str(highest[i]) + ',' +
                            str(longest[i]) + ',' +
                            str(count[i]) + ',' +
                            str(forces[i]) + ',' +
                            str(area[i]) + ',' +
                            str(gravity[i]) + ',')
            outfd.write(str(highest[R] - highest[L]) + ',' +
                        str(longest[R] - longest[L]) + ',' +
                        str(count[R] - count[L]) + ',' + str(count[L])+'_'+str(count[R]) + ',' +
                        str(count[R] / float(count[R] + count[L])) + ',' +
                        str(forces[R] / float(forces[R] + forces[L])) + ',' +
                        str(area[R] / sum_area) + ',' +
                        str(gravity[R] - gravity[L]) + ',')
        outfd.write('L\n' if catg == L else 'R\n')
        last_data = data

output_filename = '..\Sentons_Result\data_analyse.txt'
outfd = open(output_filename, 'w')
outfd.write('User,Mission,Total(Area*Force),')
for i in range(2):
    outfd.write(bar_catg[i] + '(Highest),' +
                bar_catg[i] + '(Longest),' +
                bar_catg[i] + '(Count),' +
                bar_catg[i] + '(Force),' +
                bar_catg[i] + '(Area*Force),' +
                bar_catg[i] + '(Gravity),')
outfd.write('R-L(Highest),R-L(Longest),')
outfd.write('R-L(Count),L_R(Count),RightPortion(Count),')
outfd.write('RightPortion(Force),')
outfd.write('RightPortion(Area*Force),')
outfd.write('R-L(Gravity),')
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