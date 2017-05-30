import sys
import os.path
from data_format import PIXELS
from data_format import data_to_edge

import numpy as np
from sklearn import svm
from sklearn import tree
from sklearn import neighbors
from sklearn.externals import joblib
from sklearn.model_selection import KFold

category = [[] for i in range(3)]
category[0] = ['H_L', 'H_L_F', 'H_L_A']
category[1] = ['H_R', 'H_R_F', 'H_R_A']
#category[2] = ['H_D', 'H_D_F', 'H_D_A']
#category[0] = ['H_L', 'H_L_F', 'H_L_A']
#category[1] = ['H_R', 'H_R_F', 'H_R_A']
#category[0] = ['V_L', 'V_L_F', 'V_L_A']
#category[1] = ['V_R', 'V_R_F', 'V_R_A']

duplicate_removal = False
zero_removal = True

X = [[]]
raw_data = [[]]
y = [[]]


def process(fd, catg, user_id):
    lines = fd.readlines()
    last_data = []
    for line in lines[2:]:
        data = line[:-1].split(' ')[2:]
        if duplicate_removal and cmp(data, last_data) == 0:
            continue
        last_data = data
        n, edge = data_to_edge(data)
        if zero_removal and n <= 0:
            continue
        X[user_id].append(edge)
        y[user_id].append(catg)
        raw_data[user_id].append(data)


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
                        raw_data.append([])
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
            X_test = []
            X_train = []
            y_train = []
            for j in range(len(X)):
                for data in raw_data[j]:
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
                    features = []
                    for bar in range(2):
                        if area[bar] != 0:
                            gravity[bar] /= area[bar]
                        features.append(gravity[bar])
                        features.append(lowest[bar])
                        features.append(highest[bar])

                    #features = [gravity]
                    if i == j:
                        X_test.append(features)
                    else:
                        X_train.append(features)
                if i == j:
                    y_test = y[j]
                else:
                    y_train.extend(y[j])
                '''
                if i == j:
                    X_test = X[j]
                    y_test = y[j]
                else:
                    X_train.extend(X[j])
                    y_train.extend(y[j])
                '''
            print 'Start training on ' + str(len(X_train)) + ' data'
            clf = tree.DecisionTreeClassifier()
            # clf = neighbors.KNeighborsClassifier(100, 'distance', 'auto', p=1)
            clf.fit(X_train, y_train)
            answer_train = clf.predict(X_train)
            print('training accuracy: ' + str(np.mean(answer_train == y_train)))
            answer_test = clf.predict(X_test)
            print('test accuracy: ' + str(np.mean(answer_test == y_test)))
            acc.append(np.mean(answer_test == y_test))
            print
        print "Final accuracy: " + str(np.mean(acc))


    def feature_calc(split):
        acc = []
        print "Split: " + str(split)
        for i in range(len(X)):
            y_test = y[i]
            answer_test = []

            for data in raw_data[i]:
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
            '''
            for data in X[i]:
                gravity = 0
                tot = 0
                for j in range(PIXELS):
                    gravity += (data[j] + data[j+PIXELS]) * j
                    tot += data[j] + data[j+PIXELS]
                gravity /= tot
            '''

            answer_test = np.array(answer_test)
            print('test accuracy: ' + str(np.mean(answer_test == y_test)))
            acc.append(np.mean(answer_test == y_test))
        print "Final accuracy: " + str(np.mean(acc))
        print

    machine_learning()
    #for i in range(40, 80, 1):
        #feature_calc(i)


def all_user_test():
    X_tot = []
    y_tot = []

    for i in range(len(X)):
        X_tot.extend(X[i])
        y_tot.extend(y[i])
    X_tot = np.array(X_tot)
    y_tot = np.array(y_tot)

    print 'Start training on ' + str(len(X_tot)) + ' data'
    sys.stdout.flush()

    kf = KFold(n_splits=5, shuffle=True)
    kf.get_n_splits(X)
    error = []
    for k, (train_index, test_index) in enumerate(kf.split(X_tot, y_tot)):
        print('\n' + str(k))
        X_train, X_test = X_tot[train_index], X_tot[test_index]
        y_train, y_test = y_tot[train_index], y_tot[test_index]
        clf = tree.DecisionTreeClassifier(max_leaf_nodes=32)
        clf.fit(X_train, y_train)
        print('clf.fit(X_train, y_train) finish')
        answer_train = clf.predict(X_train)
        print('training accuracy: ' + str(np.mean(answer_train == y_train)))
        answer_test = clf.predict(X_test)
        print('test accuracy: ' + str(np.mean(answer_test == y_test)))
        error.append(np.mean(answer_test == y_test))

        # Averaging
    print "===========Final Result==========="
    print "Final accuracy: " + str(np.mean(error))


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




