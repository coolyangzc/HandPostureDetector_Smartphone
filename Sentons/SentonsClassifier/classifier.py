import sys
import random
import numpy as np
from sklearn import svm
from sklearn import tree
from sklearn import neighbors
from sklearn.externals import joblib
from sklearn.model_selection import KFold

print 'File reading...'
sys.stdout.flush()

filename = '..\Sentons_Result\data_unique.txt'
fd = file(filename)
pixels = int(fd.readline()[:-1])

lines = fd.readlines()
#random.shuffle(lines)

X = [[]]
y = [[]]

for line in lines:
    data = line.split(' ')
    i = int(data[0])
    while i >= len(X):
        X.append([])
        y.append([])
    X[i].append(map(float, data[:-1]))
    y[i].append(int(data[-1]))

tot_data = 0
for i in range(len(X)):
    tot_data += len(X[i])
print 'Loaded ' + str(tot_data) + ' data successfully'

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
    clf = tree.DecisionTreeClassifier(max_leaf_nodes = 32)
    #clf = neighbors.KNeighborsClassifier(100, 'distance', 'auto', p=1)
    clf.fit(X_train, y_train)
    print 'Start training on ' + str(len(X_train)) + ' data'
    print('clf.fit(X_train, y_train) finish')
    answer_train = clf.predict(X_train)
    print('training accuracy: ' + str(np.mean(answer_train == y_train)))
    answer_test = clf.predict(X_test)
    print('test accuracy: ' + str(np.mean(answer_test == y_test)))

'''
X = X[:]
y = y[:]
X = np.array(X)
y = np.array(y)

print 'Start training on ' + str(len(X)) + ' data'
sys.stdout.flush()


kf = KFold(n_splits = 5, shuffle = True)
kf.get_n_splits(X)
error = []
for k, (train_index, test_index) in enumerate(kf.split(X, y)):
    print('\n' + str(k))
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    #clf = svm.SVC()
    #clf = neighbors.KNeighborsClassifier(100, 'distance', 'auto', p=1)
    clf = tree.DecisionTreeClassifier()
    clf.fit(X_train, y_train)
    print('clf.fit(X_train, y_train) finish')
    answer_train = clf.predict(X_train)      
    print('training accuracy: '+ str(np.mean(answer_train == y_train)))
    answer_test = clf.predict(X_test)
    print('test accuracy: ' + str(np.mean(answer_test == y_test)))
    error.append(np.mean(answer_test == y_test))    
    
# Averaging
print "===========Final Result==========="
print "Final accuracy: " + str(np.mean(error))
'''

#Support Vector Machine
'''
clf = svm.SVC()
clf.fit(X, y)
joblib.dump(clf, 'svm.pkl')
'''

#K Nearest Neighbors
'''
clf = neighbors.KNeighborsClassifier(100, 'distance', 'auto', p = 1)
clf.fit(X, y)
joblib.dump(clf, 'knn.pkl')
'''

#Decision Trees
'''
clf = tree.DecisionTreeClassifier()
clf.fit(X, y)
joblib.dump(clf, 'dts.pkl')
'''