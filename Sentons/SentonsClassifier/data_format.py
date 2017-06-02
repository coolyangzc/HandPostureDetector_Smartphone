EDGE_MM = 116
CONST = False
PIXELS = 128

#bar: L = 1, R = 0
#pos: Up = 116, Down = 0

class features:
    def __init__(self):
        chars = ['area', 'forces', 'count', 'gravity', 'lowest_long', 'highest', 'longest']
        for char in chars: setattr(self, char, [0,0])
        self.lowest = [116, 116]


class identifiers:
    def __init__(self):

def data_to_edge(data):
    n = int(data[0])
    n_zero = 0
    edge = [0 for i in range(PIXELS) * 2]
    p = 1
    for touch in range(n):
        bar = int(data[p])
        force = int(data[p+2])
        pos0 = float(data[p+4])
        pos1 = float(data[p+5])
        if force == 0:
            n_zero +=1
            continue

        if CONST:
            pos0 = int(round(pos0 / EDGE_MM * (PIXELS - 1)))
            pos1 = int(round(pos1 / EDGE_MM * (PIXELS - 1)))
            for i in range(pos0, pos1 + 1):
                edge[bar * PIXELS + i] += force
        else:
            def trapezoid(l, r):
                if l == r:
                    return 0
                lH = force - abs(mPos - l) * k
                rH = force - abs(mPos - r) * k
                return (lH + rH) * (r - l) / 2
            pos0 = pos0 / EDGE_MM * PIXELS
            pos1 = pos1 / EDGE_MM * PIXELS
            mPos = (pos0 + pos1) / 2

            k = force * 0.9 / (mPos - pos0)
            l = int(pos0)
            r = min(int(pos1) + 1, PIXELS - 1)
            for i in range(l, r + 1):
                id = bar * PIXELS + i
                if i+1 <= pos0 or i >= pos1:
                    continue
                if i + 1 < mPos:
                    if i < pos0:
                        edge[id] += trapezoid(pos0, i+1)
                    else:
                        edge[id] += trapezoid(i, i+1)
                else:
                    if i < mPos:
                        edge[id] += trapezoid(i, mPos) + trapezoid(mPos, i+1)
                    else:
                        if i+1 < pos1:
                            edge[id] += trapezoid(i, i+1)
                        else:
                            edge[id] += trapezoid(i, pos1)
        p += 6
    n -= n_zero
    return n, edge


def data_to_features(data):
    n = int(data[0])
    f = features()
    p = 1
    for touch in range(n):
        bar = int(data[p]) ^ 1
        force = int(data[p + 2])
        pos0 = float(data[p + 4])
        pos1 = float(data[p + 5])
        if force == 0:
            continue
        f.count[bar] += 1
        f.forces[bar] += force
        f.area[bar] += force * (pos1 - pos0)
        f.gravity[bar] += force * (pos1 - pos0) * (pos0 + pos1) / 2
        if pos0 < f.lowest[bar]:
            f.lowest[bar] = pos0
            f.lowest_long[bar] = pos1 - pos0
        f.highest[bar] = max(f.highest[bar], pos1)
        f.longest[bar] = max(f.longest[bar], pos1 - pos0)
        p += 6
    for i in range(2):
        if f.area[bar] > 0:
            f.gravity[bar] /= f.area[bar]
    return f


