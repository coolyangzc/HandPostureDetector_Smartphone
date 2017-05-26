import sys
import random
import numpy as np
from sklearn import svm
from sklearn import tree
from sklearn import neighbors
from sklearn.externals import joblib
from sklearn.model_selection import KFold

X = [[]]
y = [[]]


def load_data():
    print 'File reading...'

    filename = '..\Sentons_Result\data_unique.txt'
    fd = file(filename)
    pixels = int(fd.readline()[:-1])

    lines = fd.readlines()
    # random.shuffle(lines)

    for line in lines:
        data = line.split(' ')
        i = int(data[0])
        while i >= len(X):
            X.append([])
            y.append([])
        X[i].append(map(float, data[1:-1]))
        y[i].append(int(data[-1]))
    print len(X[0][0])
    tot_data = 0
    for i in range(len(X)):
        tot_data += len(X[i])
    print 'Loaded ' + str(tot_data) + ' data successfully'


def new_user_test():
    acc = []
    for i in range(len(X)):
        X_train = []
        y_train = []
        for j in range(len(X)):
            if i == j:
                X_test = X[j]
                y_test = y[j]
            else:
                X_train.extend(X[j])
                y_train.extend(y[j])
        print 'Start training on ' + str(len(X_train)) + ' data'
        clf = tree.DecisionTreeClassifier(max_leaf_nodes=32)
        # clf = neighbors.KNeighborsClassifier(100, 'distance', 'auto', p=1)
        clf.fit(X_train, y_train)
        answer_train = clf.predict(X_train)
        print('training accuracy: ' + str(np.mean(answer_train == y_train)))
        answer_test = clf.predict(X_test)
        print('test accuracy: ' + str(np.mean(answer_test == y_test)))
        acc.append(np.mean(answer_test == y_test))
        print
    print "Final accuracy: " + str(np.mean(acc))


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
#new_user_test()
#all_user_test()
train_model()



