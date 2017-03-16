EDGE_MM = 116
PIXELS = 116

def data_to_edge(data):
    n = int(data[0])
    edge = [0 for i in range(PIXELS) * 2]
    p = 1
    for i in range(n):
        bar = int(data[p])
        force = int(data[p+2])
        pos0 = float(data[p+4])
        pos1 = float(data[p+5])
        pos0 = int(round(pos0 / EDGE_MM * (PIXELS - 1)))
        pos1 = int(round(pos1 / EDGE_MM * (PIXELS - 1)))
        for i in range(pos0, pos1 + 1):
            edge[bar * PIXELS + i] += force
        p += 6
    return n, edge