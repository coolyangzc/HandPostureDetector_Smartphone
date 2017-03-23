import httplib
from data_format import data_to_edge
from sklearn.externals import joblib

clf = joblib.load('dts.pkl')

print 'model loaded successfully'

while True:
    httpClient = httplib.HTTPConnection('127.0.0.1', 8000, timeout=10)
    httpClient.request('GET', '/t')
    response = httpClient.getresponse()
    data = response.read().split(' ')
    
    n, edge = data_to_edge(data)
    if n == 0:
        result = -1
    else:
        edges = [edge]
        result = clf.predict(edges)[0]
    #print result
    
    httpClient.request('GET', '/' + str(result));
    response = httpClient.getresponse()
