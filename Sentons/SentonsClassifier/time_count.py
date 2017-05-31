import os.path
import numpy as np

dir = "..\Sentons_Data"

category = [[] for i in range(3)]

category[0] = ['V_L', 'V_L_F', 'V_L_A', 'V_LR_A']
category[1] = ['V_R', 'V_R_F', 'V_R_A']
'''
category[0] = ['H_L', 'H_L_F', 'H_L_A', 'H_LR_A']
category[1] = ['H_R', 'H_R_F', 'H_R_A']
category[2] = ['H_D', 'H_D_F', 'H_D_A']
'''

FRAME_SKIP_L, FRAME_SKIP_R = 50, 50

feature_name = ['TOTAL(with Empty)', 'Empty']
hand_name = ['L', 'R', 'D', 'Sum']
category_name = ['Normal', 'Force', 'Dynamic', 'Sum']
cover_time = [[([0] * 4) for i in range(4)] for i in range(len(feature_name))]

TOTAL = 0
EMPTY = 1

frame_times = []

def analyse(fd, hand, mission, username):
    task = 0 #LR
    for i in range(3):
        if mission == category[hand][i]:
            task = i
            break
    lines = fd.readlines()
    last_data = []
    time = -1
    for line in lines[2 + FRAME_SKIP_L: -FRAME_SKIP_R]:
        last_time = time
        time = float(line[:-1].split(' ')[1])
        data = line[:-1].split(' ')[2:]
        n = int(data[0])
        forces = 0
        p = 1
        for touch in range(n):
            force = int(data[p + 2])
            forces += force
            p += 6
        if last_time == -1:
            continue
        frame_time = time - last_time
        frame_times.append(frame_time)
        cover_time[TOTAL][hand][task] += frame_time
        if forces == 0:
            cover_time[EMPTY][hand][task] += frame_time

def output_to_file(output_filename):
    for feature in range(len(feature_name)):
        for hand in range(4):
            cover_time[feature][hand][3] = 0
        for task in range(4):
            cover_time[feature][3][task] = 0
        for hand in range(3):
            for task in range(3):
                cover_time[feature][hand][3] += cover_time[feature][hand][task]
                cover_time[feature][3][task] += cover_time[feature][hand][task]
                cover_time[feature][3][3] += cover_time[feature][hand][task]
        if cover_time[TOTAL][3][3] == 0:
            return

    outfd = open(output_filename, 'w')
    for feature in range(len(feature_name)):
        print >> outfd, '%-23s%s%18s%18s%18s' % (feature_name[feature], 'L', 'R', 'D', 'Sum')
        for task in range(len(category_name)):
            print >> outfd, '%4s%-8s' % ('', category_name[task]),
            for hand in range(len(hand_name)):
                if cover_time[feature][hand][task] != 0:
                    print >> outfd, '%8.2fs, %5.1f%%' % \
                                    (cover_time[feature][hand][task] / 1000,
                                     cover_time[feature][hand][task] / cover_time[TOTAL][hand][task] * 100),
                else:
                    print >> outfd, '%8.2fs, %5.1f%%' % (0, 0),
            print >> outfd, '\n'
        print >> outfd
    outfd.close()

last_user = ''
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
print np.mean(frame_times)
#output_to_file('..\Sentons_Result\\time_landscape_tot.txt')