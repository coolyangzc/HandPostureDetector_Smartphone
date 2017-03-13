import sys
import random
import numpy as np
from sklearn import svm
from sklearn.model_selection import KFold

filename = '..\Sentons_Data\data.txt'
fd = file(filename)
pixels = int(fd.readline()[:-1])
lines = fd.readlines()
X = []
y = []

print 'File reading...'
sys.stdout.flush()
for line in lines:
    data = map(int, line.split(' '))
    X.append(data[:-1])
    y.append(data[-1])
random.shuffle(X)
random.shuffle(y)

X = X[:2000]
y = y[:2000]

X = np.array(X)
y = np.array(y)

print 'SVM training...'
sys.stdout.flush()

kf = KFold(n_splits = 5, shuffle = True)
kf.get_n_splits(X)
error = []
for k, (train_index, test_index) in enumerate(kf.split(X, y)):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    clf = svm.SVC(kernel='rbf')
    clf.fit(X_train, y_train)
    answer_train = clf.predict(X_train)      
    print('training accuracy: '+ str(np.mean(answer_train == y_train)))
    answer_test = clf.predict(X_test)
    print('test accuracy: ' + str(np.mean(answer_test == y_test)))
    error.append(np.mean(answer_test == y_test))    
# Averaging
print "===========Final Result==========="
print "Final accuracy: " + str(np.mean(error))
