import os.path

dir = "..\Sentons_Data"


#bar: L = 1, R = 0
#pos: Up = 116, Down = 0

category = [[] for i in range(2)]
category[0] = ['H_L', 'H_L_F', 'H_L_A', 'H_LR_A']
category[1] = ['H_R', 'H_R_F', 'H_R_A']
#category[2] = ['V_D', 'V_D_F', 'V_D_A']

hand_name = ['L', 'R', 'Sum']
feature_name = ['TOTAL', 'Empty', 'Gravity',
                'Integration(>)', 'Integration(>1)', 'Integration(empty, >)']
TOTAL = 0
EMPTY = 1
INTEGRATION_EMPTY = -1
category_name = ['Normal', 'Force', 'Dynamic', 'Sum']

bar_catg = ['L', 'R']

cover_time = [[([0] * 4) for i in range(3)] for i in range(len(feature_name))]
acc_time = [[([0] * 4) for i in range(3)] for i in range(len(feature_name))]
tot_cover_time = [[([0] * 4) for i in range(3)] for i in range(len(feature_name))]
tot_acc_time = [[([0] * 4) for i in range(3)] for i in range(len(feature_name))]
acc_and_cover_rate = [[[[] for i in range(4)] for i in range(3)] for i in range(len(feature_name))]

FRAME_SKIP_L, FRAME_SKIP_R = 50, 50
duplicate_removal = False
zero_removal = True


def analyse(fd, hand, mission, username):

    def calc_feature(used_feature):
        feature = feature_name[used_feature]
        if feature == 'TOTAL':
            return hand
        if feature == 'Gravity':
            if gravity_both <= 69.35:
                return 1
            else:
                return 0
        if feature == 'Integration(>)':
            for i in range(2):
                if predict[i] > predict[i^1]:
                    return i
        if feature == 'Integration(>1)':
            for i in range(2):
                if predict[i] > predict[i^1] + 1:
                    return i
        if feature == 'Empty' or 'Integration(empty, >)':
            return -1
        return -1
    task = 0
    for i in range(3):
        if mission == category[hand][i]:
            task = i
            break
    lines = fd.readlines()
    last_data = []
    time = -1
    predict = [0, 0]
    for line in lines[2 + FRAME_SKIP_L: -FRAME_SKIP_R]:
        last_time = time
        time = float(line[:-1].split(' ')[1])
        data = line[:-1].split(' ')[2:]
        if duplicate_removal and cmp(data, last_data) == 0:
            continue
        n = int(data[0])
        area, forces, count, gravity, lowest_long, highest, longest = ([0, 0] for i in range(7))
        gravity_both, area_both = 0, 0
        lowest = [116, 116]
        p = 1
        for touch in range(n):
            bar = int(data[p]) ^ 1
            force = int(data[p + 2])
            pos0 = float(data[p + 4])
            pos1 = float(data[p + 5])
            count[bar] += 1
            forces[bar] += force
            area_both += force * (pos1 - pos0)
            gravity_both += force * (pos1 - pos0) * (pos0 + pos1) / 2
            area[bar] += force * (pos1 - pos0)
            gravity[bar] += force * (pos1 - pos0) * (pos0 + pos1) / 2
            if pos0 < lowest[bar]:
                lowest[bar] = pos0
                lowest_long[bar] = pos1 - pos0
            highest[bar] = max(highest[bar], pos1)
            longest[bar] = max(longest[bar], pos1 - pos0)
            p += 6
        if last_time == -1:
            continue
        frame_time = time - last_time
        sum_area = area[0] + area[1]
        if zero_removal and sum_area == 0:
            cover_time[EMPTY][hand][task] += frame_time
            acc_time[EMPTY][hand][task] += frame_time
            for i in range(2):
                if predict[i] > predict[i^1]:
                    cover_time[INTEGRATION_EMPTY][hand][task] += frame_time
                    if hand == i:
                        acc_time[INTEGRATION_EMPTY][hand][task] += frame_time
            continue
        for bar in range(2):
            if area[bar] != 0:
                gravity[bar] /= area[bar]
        gravity_both /= area_both

        predict[0] = predict[1] = 0
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


def output_to_file(output_filename):
    for feature in range(len(feature_name)):
        for hand in range(3):
            cover_time[feature][hand][3] = 0
            acc_time[feature][hand][3] = 0
        for task in range(4):
            cover_time[feature][2][task] = 0
            acc_time[feature][2][task] = 0
        for hand in range(2):
            for task in range(3):
                cover_time[feature][hand][3] += cover_time[feature][hand][task]
                cover_time[feature][2][task] += cover_time[feature][hand][task]
                cover_time[feature][2][3] += cover_time[feature][hand][task]
                acc_time[feature][hand][3] += acc_time[feature][hand][task]
                acc_time[feature][2][task] += acc_time[feature][hand][task]
                acc_time[feature][2][3] += acc_time[feature][hand][task]
        if cover_time[TOTAL][2][3] == 0:
            return
        for hand in range(len(hand_name)):
            for task in range(len(category_name)):
                cover_rate = cover_time[feature][hand][task] / cover_time[TOTAL][hand][task]
                if cover_time[feature][hand][task] > 0:
                    acc_rate = acc_time[feature][hand][task] / cover_time[feature][hand][task]
                else:
                    acc_rate = 0
                acc_and_cover_rate[feature][hand][task].append((acc_rate, cover_rate))

    outfd = open(output_filename, 'w')
    for feature in range(len(feature_name)):
        print >> outfd, '%-23s%s%18s%18s' % (feature_name[feature], 'L', 'R', 'Sum')
        for task in range(len(category_name)):
            print >> outfd, '%4s%-8s' % ('', category_name[task]),
            for hand in range(len(hand_name)):
                print >> outfd, '%8.2fs, %6.2f%%' % \
                                (cover_time[feature][hand][task] / 1000,
                                 cover_time[feature][hand][task] / cover_time[TOTAL][hand][task] * 100),
            print >> outfd, '\n%12s' % '',
            for hand in range(len(hand_name)):
                print >> outfd, '%8.2fs,' % (acc_time[feature][hand][task] / 1000),
                if cover_time[feature][hand][task] > 0:
                    print >> outfd, '%6.2f%%' % \
                                    (acc_time[feature][hand][task] / cover_time[feature][hand][task] * 100),
                else:
                    print >> outfd, '%6.2f%%' % 0,
            print >> outfd, '\n'
        print >> outfd
    outfd.close()

def output_rate(output_filename):
    outfd = open(output_filename, 'w')

    for feature in range(len(feature_name)):
        print >> outfd, '%s' % feature_name[feature]
        for task in range(len(category_name)):
            for hand in range(len(hand_name)):
                print >> outfd, '%4s%-8s%-8s' % ('', category_name[task], hand_name[hand]),
                acc_and_cover_rate[feature][hand][task].sort()
                for pair in acc_and_cover_rate[feature][hand][task]:
                    print >> outfd, '%6.2f%%' % float(pair[0] * 100),
                print >> outfd
                print >> outfd, '%20s' % '',
                for pair in acc_and_cover_rate[feature][hand][task]:
                    print >> outfd, '%6.2f%%' % float(pair[1] * 100),
                print >> outfd
                print >> outfd

        print >> outfd
    outfd.close()

last_user = ''
for parent, dirnames, filenames in os.walk(dir):
    for filename in filenames:
        user = parent.split('\\')[-1]
        if user != last_user and last_user != '':
            output_to_file('..\Sentons_Result\\landscape\\feature_cover_' + last_user + '.txt')
            for feature in range(len(feature_name)):
                for hand in range(3):
                    for task in range(4):
                        tot_cover_time[feature][hand][task] += cover_time[feature][hand][task]
                        tot_acc_time[feature][hand][task] += acc_time[feature][hand][task]
                        cover_time[feature][hand][task] = 0
                        acc_time[feature][hand][task] = 0
        fd = file(os.path.join(parent, filename))
        tag = fd.readline()
        tag = tag[:-1]
        for i in range(len(category)):
            if tag in category[i]:
                print 'Reading ' + os.path.join(parent, filename)
                analyse(fd, i, tag, parent.split('\\')[-1])
                break

        last_user = user

output_to_file('..\Sentons_Result\\landscape\\feature_cover_' + user + '.txt')

output_rate('..\Sentons_Result\\landscape\\feature_cover_sorted_rate.txt')

for feature in range(len(feature_name)):
    for hand in range(2):
        for task in range(3):
            cover_time[feature][hand][task] += tot_cover_time[feature][hand][task]
            acc_time[feature][hand][task] += tot_acc_time[feature][hand][task]

output_to_file('..\Sentons_Result\\landscape\\feature_cover_tot.txt')

