import os.path
from data_format import data_to_features

dir = "..\Sentons_Data"


#bar: L = 1, R = 0
#pos: Up = 116, Down = 0

category = [[] for i in range(2)]
category[0] = ['V_L', 'V_L_F', 'V_L_A']
category[1] = ['V_R', 'V_R_F', 'V_R_A']
#category[2] = ['V_D', 'V_D_F', 'V_D_A']

hand_name = ['L', 'R', 'Sum']
feature_name = ['TOTAL', 'Empty', 'ONE_SIDE', 'Count >= 3', 'Highest', 'Lowest_Long', 'Distinct',
                'Integration(>)', 'Integration(>1)', 'Integration(Prob,>)', 'Integration(empty, >)']
TOTAL = 0
EMPTY = 1
INTEGRATION_PROB = -2
INTEGRATION_EMPTY = -1
category_name = ['Normal', 'Force', 'Dynamic', 'Sum']

bar_catg = ['L', 'R']

acc_and_cover_rate = [[[[] for i in range(4)] for i in range(3)] for i in range(len(feature_name))]

FRAME_SKIP_L, FRAME_SKIP_R = 50, 50
duplicate_removal = False
zero_removal = True

X, y, w, f, t = ([[]] for i in range(5))
name = []


def process(fd, catg, mission, user_id):
    for hand in range(2):
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
        if duplicate_removal and cmp(data, last_data) == 0:
            continue
        last_data = data
        if last_time == -1:
            continue
        X[user_id].append(data)
        y[user_id].append(catg)
        w[user_id].append(time - last_time)
        f[user_id].append(data_to_features(data))
        t[user_id].append(task)


def load_data():
    dir = "..\Sentons_Data"
    last_parent = ''
    user_id = 0
    for parent, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            fd = file(os.path.join(parent, filename))
            tag = fd.readline()
            tag = tag[:-1]
            for i in range(len(category)):
                if tag in category[i]:
                    if parent != last_parent and last_parent != '':
                        user_id += 1
                        X.append([]), f.append([])
                        y.append([]), w.append([]), t.append([])
                    if last_parent != parent:
                        last_parent = parent
                        print 'Reading ' + parent
                        last_user = last_parent.split('\\')[-1]
                        name.append(last_user)
                    process(fd, i, tag, user_id)
                    break
    tot_data = 0
    for i in range(len(X)):
        tot_data += len(X[i])
    print 'Loaded ' + str(tot_data) + ' data from ' + str(len(X)) + ' users successfully'


def output_rate(output_filename):
    outfd = open(output_filename, 'w')

    for feature in range(len(feature_name)):
        print >> outfd, '%s' % feature_name[feature]
        for task in range(len(category_name)):
            for hand in range(len(hand_name)):
                print >> outfd, '%4s%-8s%-8s' % ('', category_name[task], hand_name[hand]),
                acc_and_cover_rate[feature][hand][task].sort()
                for pair in acc_and_cover_rate[feature][hand][task]:
                    print >> outfd, '%5.1f%%' % float(pair[0] * 100),
                print >> outfd
                print >> outfd, '%20s' % '',
                for pair in acc_and_cover_rate[feature][hand][task]:
                    print >> outfd, '%5.1f%%' % float(pair[1] * 100),
                print >> outfd
                print >> outfd

        print >> outfd
    outfd.close()


def output_to_file(output_filename, X, y, w, fs, t):
    cover_time = [[([0] * 4) for i in range(3)] for i in range(len(feature_name))]
    acc_time = [[([0] * 4) for i in range(3)] for i in range(len(feature_name))]
    f_acc_rate = [([0] * 2) for i in range(len(feature_name))]

    def calc_feature(used_feature):
        feature = feature_name[used_feature]
        if feature == 'TOTAL':
            return hand
        if feature == 'ONE_SIDE':
            for i in range(2):
                if f.count[i] == 0:
                    return i ^ 1
        if feature == 'Count >= 3':
            for i in range(2):
                if f.count[i] >= 3 > f.count[i ^ 1]:
                    return i ^ 1
        if feature == 'Highest':
            for i in range(2):
                if f.highest[i] >= 95 > 90 > f.highest[i ^ 1]:
                    return i
        if feature == 'Lowest_Long':
            for i in range(2):
                if f.lowest[i] <= 18 and f.lowest[i ^ 1] <= 30:
                    if f.lowest_long[i] >= 22 and 0 < f.lowest_long[i ^ 1] <= 14:
                        return i
        if feature == 'Distinct':
            for i in range(2):
                if f.distinct[i] > f.distinct[i ^ 1] == 1:
                    return i ^ 1
        if feature == 'Integration(>)':
            for i in range(2):
                if predict[i] > predict[i ^ 1]:
                    return i
        if feature == 'Integration(>1)':
            for i in range(2):
                if predict[i] > predict[i ^ 1] + 1:
                    return i
        if feature == 'Empty' or 'Integration(empty, >)':
            return -1
        return -1

    predict = [0, 0]
    for i in range(len(X)):
        data = X[i]
        if duplicate_removal and cmp(data, last_data) == 0:
            continue
        last_data = data
        hand, task, f, frame_time = y[i], t[i], fs[i], w[i]
        if zero_removal and (f.area[0] + f.area[1]) == 0:
            cover_time[EMPTY][hand][task] += frame_time
            acc_time[EMPTY][hand][task] += frame_time
            for i in range(2):
                if predict[i] > predict[i ^ 1]:
                    cover_time[INTEGRATION_EMPTY][hand][task] += frame_time
                    if hand == i:
                        acc_time[INTEGRATION_EMPTY][hand][task] += frame_time
            continue
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

    for feature in range(len(feature_name)):
        for hand in range(2):
            for task in range(3):
                cover_time[feature][hand][3] += cover_time[feature][hand][task]
                cover_time[feature][2][task] += cover_time[feature][hand][task]
                cover_time[feature][2][3] += cover_time[feature][hand][task]
                acc_time[feature][hand][3] += acc_time[feature][hand][task]
                acc_time[feature][2][task] += acc_time[feature][hand][task]
                acc_time[feature][2][3] += acc_time[feature][hand][task]
        for hand in range(2):
            hand_time = acc_time[feature][hand][3] + cover_time[feature][hand^1][3] - acc_time[feature][hand^1][3]
            if hand_time > 0:
                f_acc_rate[feature][hand] = (acc_time[feature][hand][3]) / hand_time
        if cover_time[TOTAL][2][3] == 0:
            return
    predict = [0, 0]
    for i in range(len(X)):
        data = X[i]
        if duplicate_removal and cmp(data, last_data) == 0:
            continue
        last_data = data
        hand, task, f, frame_time = y[i], t[i], fs[i], w[i]
        if zero_removal and (f.area[0] + f.area[1]) == 0:
            continue
        predict[0] = predict[1] = 0
        for feature in range(len(feature_name)):
            if feature_name[feature] == 'TOTAL':
                continue
            if feature_name[feature].startswith('Integration'):
                break
            res = calc_feature(feature)
            if res != -1:
                predict[res] += f_acc_rate[feature][res]
        for i in range(2):
            if predict[i] > predict[i^1]:
                cover_time[INTEGRATION_PROB][hand][task] += frame_time
                if hand == i:
                    acc_time[INTEGRATION_PROB][hand][task] += frame_time

    feature = INTEGRATION_PROB
    for hand in range(2):
        for task in range(3):
            cover_time[feature][hand][3] += cover_time[feature][hand][task]
            cover_time[feature][2][task] += cover_time[feature][hand][task]
            cover_time[feature][2][3] += cover_time[feature][hand][task]
            acc_time[feature][hand][3] += acc_time[feature][hand][task]
            acc_time[feature][2][task] += acc_time[feature][hand][task]
            acc_time[feature][2][3] += acc_time[feature][hand][task]
    for feature in range(len(feature_name)):
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

        print >> outfd, '\\begin{table}[H]\n\centering\n\caption{title}\n%\label{tab:chap4}'
        print >> outfd, '\\begin{tabular}{c|c|c|c|c|c|c}\n\\toprule[2pt]'
        print >> outfd, '\multirow{2}{*}{} & \multicolumn{3}{c|}{cover} & \multicolumn{3}{c}{correct} \\\\'
        print >> outfd, '\cline{2-7} & Left & Right & Sum & Left & Right & Sum \\\\ \midrule[1pt]'

        for task in range(len(category_name)):
            print >> outfd, '%s ' % (category_name[task]),
            for hand in range(len(hand_name)):
                print >> outfd, "& %.1f\%%" % (cover_time[feature][hand][task] / cover_time[TOTAL][hand][task] * 100),
            for hand in range(len(hand_name)):
                if cover_time[feature][hand][task] > 0:
                    print >> outfd, "& %.1f\%%" % (
                    acc_time[feature][hand][task] / cover_time[feature][hand][task] * 100),
                else:
                    print >> outfd, "& 0.0%%",
            print >> outfd, '\\\\',
            if task != len(category_name) - 1:
                print >> outfd, '\hline',
            print >> outfd

        print >> outfd, '\\bottomrule[2pt]\n\end{tabular}\n\end{table}'
        print >> outfd, '\n\n'

    for feature in range(len(feature_name)):
        print >> outfd, feature_name[feature]
        for hand in range(2):
            print >> outfd, f_acc_rate[feature][hand],
        print >> outfd
    outfd.close()



load_data()

X_tot, y_tot, w_tot, f_tot, t_tot = ([] for i in range(5))
for i in range(len(X)):
    output_to_file('..\Sentons_Result\\feature_cover_' + name[i] + '.txt', X[i], y[i], w[i], f[i], t[i])
    X_tot.extend(X[i])
    y_tot.extend(y[i])
    w_tot.extend(w[i])
    f_tot.extend(f[i])
    t_tot.extend(t[i])
output_rate('..\Sentons_Result\\feature_cover_sorted_rate.txt')
output_to_file('..\Sentons_Result\\feature_cover_tot.txt', X_tot, y_tot, w_tot, f_tot, t_tot)

