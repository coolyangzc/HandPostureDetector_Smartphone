import sys
import os.path
from data_format import data_to_edge
from data_format import data_to_features

import numpy as np
from sklearn import svm
from sklearn import tree
from sklearn import neighbors
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.externals import joblib
from sklearn.model_selection import KFold

category = [[] for i in range(3)]

category[0] = ['V_L', 'V_L_F', 'V_L_A']
category[1] = ['V_R', 'V_R_F', 'V_R_A']

eps = 1e-8
duplicate_removal = False
zero_removal = True

feature_name = ['ONE_SIDE', 'Count >= 3', 'Highest >= 95', 'Lowest_Long',
                'Integration(>)', 'Integration(>1)', 'Integration(empty, >)']

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
                    if parent != last_parent and last_parent != '':
                        user_id += 1
                        X.append([])
                        y.append([])
                        weight.append([])
                    if last_parent != parent:
                        last_parent = parent
                        print 'Reading ' + parent
                    process(fd, i, user_id)
                    break
    tot_data = 0
    for i in range(len(X)):
        tot_data += len(X[i])
    print 'Loaded ' + str(tot_data) + ' data from ' + str(len(X)) + ' users successfully'
    sys.stdout.flush();


def new_user_test():

    prob_time, tot_time = [0, 0, 0], [0, 0, 0]
    prob_matrix = [[0, 0], [0, 0]]

    def machine_learning():
        acc = []
        for i in range(len(X)):
            X_train, y_train, w_train = ([] for i in range(3))
            X_test, y_test, w_test = ([] for i in range(3))

            for j in range(len(X)):
                for data in X[j]:
                    n = int(data[0])
                    area, forces, count, gravity, lowest_long, highest, longest = ([0, 0] for i in range(7))
                    lowest = [116, 116]
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
                    features = []
                    for bar in range(2):
                        if area[bar] != 0:
                            gravity[bar] /= area[bar]
                        #features.append(gravity[bar])
                        features.append(count[bar])
                        features.append(highest[bar])
                        features.append(lowest[bar])
                        features.append(lowest_long[bar])
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
            clf = tree.DecisionTreeClassifier(max_leaf_nodes=128)
            #clf = RandomForestClassifier(n_estimators=100, max_leaf_nodes=8)
            #clf = neighbors.KNeighborsClassifier(100, 'distance', 'auto', p=1)
            #clf = GradientBoostingClassifier(n_estimators=100, max_leaf_nodes=8)
            clf.fit(X_train, y_train, w_train)
            print clf.feature_importances_
            print 'training accuracy: ' + str(clf.score(X_train, y_train, w_train))

            prob = clf.predict_proba(X_test)
            test_res = clf.predict(X_test)
            for i in range(len(prob)):
                tot_time[y_test[i]] += w_test[i]
                if max(prob[i][0], prob[i][1]) >= 0.98:
                    prob_time[y_test[i]] += w_test[i]
                    prob_matrix[test_res[i]][y_test[i]] += w_test[i]

            #test_acc = clf.score(X_test, y_test, w_test)
            #print 'test accuracy: ' + str(test_acc)
            #acc.append(test_acc)
            print
        #print "Final accuracy: " + str(np.mean(acc))

    def feature_calc():
        def calc_feature(used_feature):
            feature = feature_name[used_feature]
            if feature == 'ONE_SIDE':
                for i in range(2):
                    if f.count[i] == 0:
                        return i ^ 1
            if feature == 'Count >= 3':
                for i in range(2):
                    if f.count[i] >= 3 > f.count[i ^ 1]:
                        return i ^ 1
            if feature == 'Highest >= 95':
                for i in range(2):
                    if f.highest[i] >= 95 > f.highest[i ^ 1]:
                        return i
            if feature == 'Lowest_Long':
                for i in range(2):
                    if f.lowest[i] <= 15 and f.lowest[i ^ 1] <= 15:
                        if f.lowest_long[i] >= 24 and 0 < f.lowest_long[i ^ 1] <= 15:
                            return i
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

        X_test, y_test, w_test = [], [], []
        for i in range(len(X)):
            X_test.extend(X[i])
            y_test.extend(y[i])
            w_test.extend(weight[i])
        for i in range(len(X_test)):
            f = data_to_features(X_test[i])
            tot_time[y_test[i]] += w_test[i]
            predict = [0, 0]
            for feature in range(len(feature_name)):
                res = calc_feature(feature)
                if res == -1:
                    continue
                if not feature_name[feature].startswith('Integration'):
                    predict[res] += 1
                if feature_name[feature] == 'Integration(>)':
                    prob_time[y_test[i]] += w_test[i]
                    prob_matrix[y_test[i]][res] += w_test[i]


    #machine_learning()
    feature_calc()
    for i in range(2):
        tot = 0
        for j in range(2):
            tot += prob_matrix[i][j]
        for j in range(2):
            print "%.2f%%" % (prob_matrix[i][j] / tot * 100),
        print
    tot_time[2] = tot_time[0] + tot_time[1]
    prob_time[2] = prob_time[0] + prob_time[1]
    for i in range(3):
        print "%.2f%%" % (prob_time[i] / tot_time[i] * 100),


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

load_data()
new_user_test()
#all_user_test()
#train_model()






