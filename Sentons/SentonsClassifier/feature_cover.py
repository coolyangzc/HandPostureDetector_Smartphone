import os.path

dir = "..\Sentons_Data"


#bar: L = 1, R = 0
#pos: Up = 116, Down = 0

L = 1
R = 0
category = [[] for i in range(2)]
category[0] = ['V_R', 'V_R_F', 'V_R_A']
category[1] = ['V_L', 'V_L_F', 'V_L_A']

#category[2] = ['V_D', 'V_D_F', 'V_D_A']
bar_catg = ['R', 'L']

global tot_time
tot_time = 0

ONE_SIDE = 0
cover_time = [0]
accurate_time = [0]

duplicate_removal = False
zero_removal = True


def analyse(fd, catg, mission, username):
    global tot_time
    lines = fd.readlines()
    last_data = []
    last_time = time = 0
    for line in lines[2:]:
        last_time = time
        time = float(line[:-1].split(' ')[1])
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
            bar = int(data[p])
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
        if sum_area == 0:
            if zero_removal:
                continue

        frame_time = time - last_time
        tot_time += frame_time

        for i in range(2):
            if count[i] == 0:
                cover_time[ONE_SIDE] += frame_time
                if i == catg ^ 1:
                    accurate_time[ONE_SIDE] += frame_time


        last_data = data



for parent, dirnames, filenames in os.walk(dir):
    for filename in filenames:
        fd = file(os.path.join(parent, filename))
        tag = fd.readline()
        tag = tag[:-1]
        for i in range(len(category)):
            if tag in category[i]:
                print 'Reading ' + os.path.join(parent, filename)
                analyse(fd, i, tag, parent.split('\\')[-1])
                break

output_filename = '..\Sentons_Result\\feature_cover.txt'
outfd = open(output_filename, 'w')

outfd.write('Total Valid Time: ' + str(tot_time) + '\n')
outfd.write('ONE_SIDE:\n')
outfd.write('\tCover: ' + str(cover_time[ONE_SIDE]) + ' ' + str(cover_time[ONE_SIDE] / tot_time) + '\n')
outfd.write('\tAccuracy: ' + str(accurate_time[ONE_SIDE]) + ' ' +
            str(accurate_time[ONE_SIDE] / cover_time[ONE_SIDE]) + '\n')
outfd.close()