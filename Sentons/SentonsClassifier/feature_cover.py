import os.path

dir = "..\Sentons_Data"


#bar: L = 1, R = 0
#pos: Up = 116, Down = 0

category = [[] for i in range(2)]
category[0] = ['V_L', 'V_L_F', 'V_L_A']
category[1] = ['V_R', 'V_R_F', 'V_R_A']
#category[2] = ['V_D', 'V_D_F', 'V_D_A']

hand_name = ['L', 'R', 'Sum']
feature_name = ['TOTAL', 'ONE_SIDE', 'Count >= 3', 'Highest >= 95', 'Lowest_Long',
                'Integration(>)', 'Integration(>1)']
TOTAL = 0
category_name = ['Normal', 'Force', 'Dynamic', 'Sum']

bar_catg = ['L', 'R']

cover_time = [[([0] * 4) for i in range(3)] for i in range(len(feature_name))]
acc_time = [[([0] * 4) for i in range(3)] for i in range(len(feature_name))]

FRAME_SKIP_L, FRAME_SKIP_R = 20, 20
duplicate_removal = False
zero_removal = True


def analyse(fd, hand, mission, username):

    def calc_feature(used_feature):
        feature = feature_name[used_feature]
        if feature == 'TOTAL':
            return hand
        if feature == 'ONE_SIDE':
            for i in range(2):
                if count[i] == 0:
                    return i ^ 1
        if feature == 'Count >= 3':
            for i in range(2):
                if count[i] >= 3 and count[i] > count[i^1]:
                    return i ^ 1
        if feature == 'Highest >= 95':
            for i in range(2):
                if highest[i] >= 95 > highest[i^1]:
                    return i
        if feature == 'Lowest_Long':
            for i in range(2):
                if lowest[i] <= 15 and lowest[i^1] <= 15:
                    if lowest_long[i] >= 24 and 0 < lowest_long[i^1] <= 18:
                        return i
        if feature == 'Integration(>)':
            for i in range(2):
                if predict[i] > predict[i^1]:
                    return i
        if feature == 'Integration(>1)':
            for i in range(2):
                if predict[i] > predict[i^1] + 1:
                    return i
        return -1

    for i in range(3):
        if mission == category[hand][i]:
            task = i
            break
    lines = fd.readlines()
    last_data = []
    last_time = time = -1
    for line in lines[2 + FRAME_SKIP_L: -FRAME_SKIP_R]:
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
        lowest = [116, 116]
        lowest_long = [0, 0]
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
            if pos0 < lowest[bar]:
                lowest[bar] = pos0
                lowest_long[bar] = pos1 - pos0
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
        if last_time == -1:
            continue
        frame_time = time - last_time
        predict = [0, 0]
        for feature in range(len(feature_name)):
            res = calc_feature(feature)
            if res == -1:
                continue
            if feature != 0 and not feature_name[feature].startswith('Integration'):
                predict[res] += 1
            cover_time[feature][hand][task] += frame_time
            if hand == res:
                acc_time[feature][hand][task] += frame_time
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

for feature in range(len(feature_name)):
    for hand in range(2):
        for task in range(3):
            cover_time[feature][hand][3] += cover_time[feature][hand][task]
            cover_time[feature][2][task] += cover_time[feature][hand][task]
            cover_time[feature][2][3] += cover_time[feature][hand][task]
            acc_time[feature][hand][3] += acc_time[feature][hand][task]
            acc_time[feature][2][task] += acc_time[feature][hand][task]
            acc_time[feature][2][3] += acc_time[feature][hand][task]

for feature in range(len(feature_name)):
    print >> outfd, '%-23s%s%18s%18s' % (feature_name[feature], 'L', 'R', 'Sum')
    for task in range(len(category_name)):
        print >> outfd, '%4s%-8s' % ('',category_name[task]),
        for hand in range(len(hand_name)):
            print >> outfd, '%8.2fs, %5.1f%%' % \
                    (cover_time[feature][hand][task] / 1000,
                     cover_time[feature][hand][task] / cover_time[TOTAL][hand][task] * 100),
        print >> outfd, '\n%12s' % '',
        for hand in range(len(hand_name)):
            print >> outfd, '%8.2fs,' % (acc_time[feature][hand][task] / 1000),
            if cover_time[feature][hand][task] > 0:
                print >> outfd, '%5.1f%%' % \
                                (acc_time[feature][hand][task] / cover_time[feature][hand][task] * 100),
            else:
                print >> outfd, '%5.1f%%' % 0,
        print >> outfd, '\n'
    print >> outfd
outfd.close()