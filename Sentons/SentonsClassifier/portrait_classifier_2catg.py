import sys
import os.path
from data_format import data_to_edge
from data_format import data_to_features
from data_format import features_to_identifiers

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

FRAME_SKIP_L, FRAME_SKIP_R = 50, 50

X = [[]]
y = [[]]
w = [[]]


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
        w[user_id].append(time - last_time)


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
                        w.append([])
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

    prob_list = []
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
                    n, edge = data_to_edge(data)
                    if i == j:
                        X_test.append(edge)
                        #X_test.append(features)
                    else:
                        X_train.append(edge)
                        #X_train.append(features)
                if i == j:
                    y_test = y[j]
                    w_test = w[j]
                else:
                    y_train.extend(y[j])
                    w_train.extend(w[j])
            print 'Start training on ' + str(len(X_train)) + ' data'
            clf = tree.DecisionTreeClassifier(max_leaf_nodes=128)
            #clf = RandomForestClassifier(n_estimators=100, max_leaf_nodes=128)
            #clf = neighbors.KNeighborsClassifier(100, 'uniform', 'kd_tree')
            #clf = GradientBoostingClassifier(n_estimators=100, max_leaf_nodes=8)
            w_train = np.array(w_train)
            clf.fit(X_train, y_train)#, w_train)
            #print clf.feature_importances_
            print 'training accuracy: ' + str(clf.score(X_train, y_train, w_train))

            prob = clf.predict_proba(X_test)
            test_res = clf.predict(X_test)
            for i in range(len(prob)):
                tot_time[y_test[i]] += w_test[i]
                prob_list.append((max(prob[i][0], prob[i][1]), y_test[i], test_res[i], w_test[i]))

            test_acc = clf.score(X_test, y_test, w_test)
            print 'test accuracy: ' + str(test_acc)
            acc.append(test_acc)
            print
        print "Final accuracy: " + str(np.mean(acc))

        prob_list.sort()
        prob_list.reverse()
        ratio = 0.1
        sum_time = tot_time[0] + tot_time[1]
        for i in range(len(prob_list)):
            pair = prob_list[i]
            prob_time[pair[1]] += pair[3]
            prob_matrix[pair[1]][pair[2]] += pair[3]
            if (prob_time[0] + prob_time[1]) >= sum_time * ratio:
                print "Ratio: " + str(ratio)
                for i in range(2):
                    tot = 0
                    for j in range(2):
                        tot += prob_matrix[i][j]
                    if tot > 0:
                        for j in range(2):
                            print "%.2f%%" % (prob_matrix[i][j] / tot * 100),
                    print
                tot_time[2] = tot_time[0] + tot_time[1]
                prob_time[2] = prob_time[0] + prob_time[1]
                for i in range(3):
                    print "%.2f%%" % (prob_time[i] / tot_time[i] * 100),
                print
                print "Accuracy: %.2f%%" % ((prob_matrix[0][0] + prob_matrix[1][1]) / (prob_time[0] + prob_time[1]) * 100)
                print
                ratio += 0.1


    def feature_calc():

        X_test, y_test, w_test = [], [], []
        for i in range(len(X)):
            X_test.extend(X[i])
            y_test.extend(y[i])
            w_test.extend(w[i])
        for i in range(len(X_test)):
            f = data_to_features(X_test[i])
            iden = features_to_identifiers(f)
            tot_time[y_test[i]] += w_test[i]
            p = iden.identifier_name.index('Integration(>)')
            if iden.result[p] != -1:
                prob_time[y_test[i]] += w_test[i]
                prob_matrix[y_test[i]][iden.result[p]] += w_test[i]

    machine_learning()
    #feature_calc()
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
        w_tot.extend(w[i])
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


def single_user_test():
    kf = KFold(n_splits=5, shuffle=True)
    user_acc = []
    for i in range(len(X)):
        X_tot = []
        for j in range(len(X[i])):
            #X_tot.append(data_to_edge(X[i][j])[1])
            f = data_to_features(X[i][j])
            X_tot.append(f.to_vector())
        X_tot = np.array(X_tot)
        y_tot = np.array(y[i])
        w_tot = np.array(w[i])

        kf.get_n_splits(X_tot)
        acc = []
        for k, (train_index, test_index) in enumerate(kf.split(X_tot, y_tot, w_tot)):
            X_train, X_test = X_tot[train_index], X_tot[test_index]
            y_train, y_test = y_tot[train_index], y_tot[test_index]
            w_train, w_test = w_tot[train_index], w_tot[test_index]
            #clf = tree.DecisionTreeClassifier(max_leaf_nodes=128)
            #clf = RandomForestClassifier(n_estimators=100, max_leaf_nodes=128)
            clf = neighbors.KNeighborsClassifier(100, 'uniform', 'kd_tree')
            clf.fit(X_train, y_train)#, w_train)
            test_acc = clf.score(X_test, y_test, w_test)
            acc.append(test_acc)
        print 'User Acc:' + str(np.mean(acc))
        user_acc.append(np.mean(acc))
    print 'Users Average Acc: %.2f%%' % (np.mean(user_acc) * 100)


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
#single_user_time_test()
single_user_test()
#new_user_test()
#all_user_test()
#train_model()






