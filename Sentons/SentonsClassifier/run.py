import httplib
from data_process import data_to_edge
from sklearn.externals import joblib

clf = joblib.load('svm.pkl') 

while True:
    httpClient = httplib.HTTPConnection('127.0.0.1', 8000, timeout=10)
    httpClient.request('GET', '/t')
    response = httpClient.getresponse()
    data = response.read().split(' ')
    
    n, edge = data_to_edge(data)
    edges = []
    edges.append(edge)
    print edges
    print clf.predict(edges)
    
    httpClient.request('GET', '/send');
    response = httpClient.getresponse()
