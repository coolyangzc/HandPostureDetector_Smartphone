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

filename = '..\Sentons_Data\data.txt'
fd = file(filename)
pixels = int(fd.readline()[:-1])

lines = fd.readlines()
random.shuffle(lines)

X = []
y = []

for line in lines:
    data = line.split(' ')
    X.append(map(float, data[:-1]))
    y.append(int(data[-1]))

print 'Loaded ' + str(len(X)) + ' data successfully'

X = X[:]
y = y[:]
X = np.array(X)
y = np.array(y)

print 'Start training on ' + str(len(X)) + ' data'
sys.stdout.flush()

'''
kf = KFold(n_splits = 5, shuffle = True)
kf.get_n_splits(X)
error = []
for k, (train_index, test_index) in enumerate(kf.split(X, y)):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]
    clf = tree.DecisionTreeClassifier()
    clf.fit(X_train, y_train)
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

clf = neighbors.KNeighborsClassifier(100, 'distance', 'auto', p = 1)
clf.fit(X, y)
joblib.dump(clf, 'knn.pkl')


#Decision Trees
'''
clf = tree.DecisionTreeClassifier()
clf.fit(X, y)
joblib.dump(clf, 'dts.pkl')
'''