import httplib

from data_format import data_to_features
from data_format import features_to_identifiers

while True:
    httpClient = httplib.HTTPConnection('127.0.0.1', 8000, timeout=10)
    httpClient.request('GET', '/t')
    response = httpClient.getresponse()
    data = response.read().split(' ')
    
    features = data_to_features(data)
    identifiers = features_to_identifiers(features)
    p = identifiers.identifier_name.index('Integration(>)')
    result = identifiers.result[p]
    #print result

    httpClient.request('GET', '/' + str(result));
    response = httpClient.getresponse()