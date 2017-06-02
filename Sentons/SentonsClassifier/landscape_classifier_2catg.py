import sys
import os.path
from data_format import PIXELS
from data_format import data_to_edge

import numpy as np
from sklearn import svm
from sklearn import tree
from sklearn import neighbors
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.externals import joblib
from sklearn.model_selection import KFold

category = [[] for i in range(3)]

category[0] = ['H_L', 'H_L_F', 'H_L_A', 'H_LR_A']
category[1] = ['H_R', 'H_R_F', 'H_R_A']
#category[2] = ['H_D', 'H_D_F', 'H_D_A']
#category[0] = ['V_L', 'V_L_F', 'V_L_A']
#category[1] = ['V_R', 'V_R_F', 'V_R_A']

eps = 1e-8
duplicate_removal = False
zero_removal = True

FRAME_SKIP_L, FRAME_SKIP_R = 50, 50

X = [[]]
y = [[]]
weight = [[]]


def process(fd, catg, user_id):
    lines = fd.readlines()
    last_data = []
    last_time = -1
    time = -1
    for line in lines[2 + FRAME_SKIP_L: -FRAME_SKIP_R]:
        last_time = time
        time = float(line[:-1].split(' ')[1])
        data = line[:-1].split(' ')[2:]
        if duplicate_removal and cmp(data, last_data) == 0:
            continue
        last_data = data
        n, edge = data_to_edge(data)
        if zero_removal and n <= 0:
            continue
        if last_time == -1:
            continue
        X[user_id].append(data)
        y[user_id].append(catg)
        weight[user_id].append(time - last_time)


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
                    print 'Reading ' + os.path.join(parent, filename)
                    if parent != last_parent and last_parent != '':
                        user_id += 1
                        X.append([])
                        y.append([])
                        weight.append([])
                    last_parent = parent
                    process(fd, i, user_id)
                    break
    tot_data = 0
    for i in range(len(X)):
        tot_data += len(X[i])
    print 'Loaded ' + str(tot_data) + ' data from ' + str(len(X)) + ' users successfully'
    sys.stdout.flush();


def new_user_test():

    def machine_learning():
        acc = []
        for i in range(len(X)):
            X_train, y_train, w_train = ([] for i in range(3))
            X_test, y_test, w_test = ([] for i in range(3))

            for j in range(len(X)):
                for data in X[j]:
                    n = int(data[0])
                    area, forces, count, ucount, dcount, gravity, longest = ([0, 0] for i in range(7))
                    #lowest = [116, 116]
                    lowest = 116
                    highest = 0
                    lowest_long = [0, 0]
                    #highest = [0, 0]
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
                        lowest = min(lowest, pos0)
                        highest = max(highest, pos1)
                        longest[bar] = max(longest[bar], pos1 - pos0)
                        if (pos1 + pos0 / 2) <= 58:
                            dcount[bar] += 1
                        else:
                            ucount[bar] += 1
                        p += 6
                    features = []
                    for bar in range(2):
                        if area[bar] != 0:
                            gravity[bar] /= area[bar]
                        features.append(gravity[bar])
                        #features.append(count[bar])
                        #features.append(dcount[bar])
                        #features.append(ucount[bar])
                    features.append(lowest)
                    features.append(highest)
                    if i == j:
                        X_test.append(features)
                    else:
                        X_train.append(features)
                if i == j:
                    y_test = y[j]
                    w_test = weight[j]
                else:
                    y_train.extend(y[j])
                    w_train.extend(weight[j])
            print 'Start training on ' + str(len(X_train)) + ' data'
            clf = tree.DecisionTreeClassifier(max_depth=2)
            #clf = RandomForestClassifier(n_estimators=100, max_leaf_nodes=8)
            #clf = neighbors.KNeighborsClassifier(100, 'distance', 'auto', p=1)
            #clf = GradientBoostingClassifier(n_estimators=100, max_leaf_nodes=8)
            clf.fit(X_train, y_train, w_train)
            print clf.feature_importances_
            print 'training accuracy: ' + str(clf.score(X_train, y_train, w_train))
            test_acc = clf.score(X_test, y_test, w_test)
            print 'test accuracy: ' + str(test_acc)
            acc.append(test_acc)
            print
        print "Final accuracy: " + str(np.mean(acc))


    def feature_calc(split):
        acc = []
        w_tot = 0
        print "Split: " + str(split)
        print 'test accuracy: ',
        for i in range(len(X)):
            y_test = y[i]
            weight_test = weight[i]
            answer_test = []
            for data in X[i]:
                area = 0
                gravity = 0
                lowest = 128
                highest = 0
                n = int(data[0])
                p = 1
                for touch in range(n):
                    bar = int(data[p])
                    force = int(data[p + 2])
                    pos0 = float(data[p + 4])
                    pos1 = float(data[p + 5])
                    if force == 0:
                        continue
                    area += force * (pos1 - pos0)
                    gravity += force * (pos1 - pos0) * (pos0 + pos1) / 2
                    lowest = min(pos0, lowest)
                    highest = max(pos1, highest)
                    p += 6
                gravity /= area
                if gravity <= split:
                    answer_test.append(1)
                else:
                    answer_test.append(0)

            answer_test = np.array(answer_test)
            test_acc = np.average(answer_test == y_test, weights = weight_test) * 100
            print "%.2f, " % test_acc,
            acc.append(test_acc * np.sum(weight_test))
            w_tot += np.sum(weight_test)
        print
        print "Final accuracy: " + str(np.sum(acc) / w_tot)
        print

    #machine_learning()
    split = 69
    while split <= 70:
        feature_calc(split)
        split += .01


def all_user_test():
    X_tot = []
    y_tot = []
    w_tot = []
    for i in range(len(X)):
        X_tot.extend(X[i])
        y_tot.extend(y[i])
        w_tot.extend(weight[i])
    X_tot = np.array(X_tot)
    y_tot = np.array(y_tot)
    w_tot = np.array(w_tot)

    print 'Start training on ' + str(len(X_tot)) + ' data'
    sys.stdout.flush()

    kf = KFold(n_splits=5, shuffle=True)
    kf.get_n_splits(X)
    acc = []
    for k, (train_index, test_index) in enumerate(kf.split(X_tot, y_tot, w_tot)):
        print('\n' + str(k))
        X_train, X_test = X_tot[train_index], X_tot[test_index]
        y_train, y_test = y_tot[train_index], y_tot[test_index]
        w_train, w_test = w_tot[train_index], w_tot[test_index]
        clf = tree.DecisionTreeClassifier(max_leaf_nodes=32)
        clf.fit(X_train, y_train, w_train)
        print('clf.fit(X_train, y_train) finish')
        print 'training accuracy: ' + str(clf.score(X_train, y_train, w_train))

        test_acc = clf.score(X_test, y_test, w_test)
        print 'test accuracy: ' + str(test_acc)
        acc.append(test_acc)

    print "===========Final Result==========="
    print "Final accuracy: " + str(np.mean(acc))


def train_model():

    X_tot = []
    y_tot = []

    for i in range(len(X)):
        X_tot.extend(X[i])
        y_tot.extend(y[i])

    # Support Vector Machine
    '''
    clf = svm.SVC()
    clf.fit(X, y)
    joblib.dump(clf, 'svm.pkl')
    '''

    # K Nearest Neighbors
    '''
    clf = neighbors.KNeighborsClassifier(100, 'distance', 'auto', p = 1)
    clf.fit(X, y)
    joblib.dump(clf, 'knn.pkl')
    '''

    # Decision Trees

    clf = tree.DecisionTreeClassifier(max_leaf_nodes=32)
    clf.fit(X_tot, y_tot)
    joblib.dump(clf, 'dts.pkl')


def calc_rate(X, y, w, target_acc):

    g = []
    for i in range(len(X)):
        data = X[i]
        n = int(data[0])
        area, gravity = 0, 0
        p = 1
        for touch in range(n):
            force = int(data[p + 2])
            pos0 = float(data[p + 4])
            pos1 = float(data[p + 5])
            if force == 0:
                continue
            area += force * (pos1 - pos0)
            gravity += force * (pos1 - pos0) * (pos0 + pos1) / 2
            p += 6
        g.append(gravity / area)

    def acc_rate(l, r):
        acc, cover = 0, 0
        for i in range(len(g)):
            if g[i] <= l:
                cover += w[i]
                if y[i] == 1:
                    acc += w[i]
            if g[i] >= r:
                cover += w[i]
                if y[i] == 0:
                    acc += w[i]
        return acc / np.sum(w), cover / np.sum(w)

    l, r, bestL, bestR = 0, 0, 0, 0
    l = 0
    while l <= 116:
        r = l + (bestR - bestL)
        while r <= 116:
            acc, cover = acc_rate(l, r)
            if acc + eps >= target_acc:
                bestL, bestR = l, r
            if cover + eps < target_acc:
                break
            r += 1
        l += 1
    l_start, l_end = bestL - 5, bestL + 5
    r_start, r_end = bestR - 5, bestR + 5
    l = l_start
    while l <= l_end:
        r = max(r_start, l + (bestR - bestL))
        while r <= r_end:
            acc, cover = acc_rate(l, r)
            if acc + eps >= target_acc:
                bestL, bestR = l, r
            if cover + eps < target_acc:
                break
            r += 0.01
        l += 0.01
    print bestL, bestR, bestR - bestL

load_data()

for i in range(len(X)):
    print i
    calc_rate(X[i], y[i], weight[i], 1.00)
#new_user_test()
#all_user_test()
#train_model()






