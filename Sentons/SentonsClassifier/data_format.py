EDGE_MM = 116
CONST = False
PIXELS = 128

#bar: L = 1, R = 0
#pos: Up = 116, Down = 0

class features:
    def __init__(self):
        chars = ['area', 'forces', 'count', 'gravity', 'lowest_long', 'highest', 'longest', 'distinct']
        for char in chars: setattr(self, char, [0,0])
        self.pos_list = [[], []]
        self.lowest = [116, 116]


class identifiers:
    def __init__(self):
        self.identifier_name = ['ONE_SIDE', 'Count >= 3', 'Highest >= 95', 'Lowest_Long', 'Distinct',
                                'Integration(>)', 'Integration(>1)']
        self.result = [0 for i in range(len(self.identifier_name))]


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
    f = features()
    n = int(data[0])
    p = 1
    for touch in range(n):
        bar = int(data[p]) ^ 1
        force = int(data[p + 2])
        pos0 = float(data[p + 4])
        pos1 = float(data[p + 5])
        if force == 0:
            continue
        f.pos_list[bar].append((pos0, pos1))
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
    for bar in range(2):
        if f.area[bar] > 0:
            f.gravity[bar] /= f.area[bar]
        f.pos_list[bar].sort()
        last_pos1 = -100
        for pos_pair in f.pos_list[bar]:
            if pos_pair[0] > 45:
                break
            if pos_pair[0] > last_pos1 + 2:
                last_pos1 = pos_pair[1]
                f.distinct[bar] += 1
    return f


def features_to_identifiers(f):

    def calc(f, identifier):
        if identifier == 'ONE_SIDE':
            for i in range(2):
                if f.count[i] > 0 and f.count[i^1] == 0:
                    return i
        if identifier == 'Count >= 3':
            for i in range(2):
                if f.count[i] >= 3 > f.count[i ^ 1]:
                    return i ^ 1
        if identifier == 'Highest >= 95':
            for i in range(2):
                if f.highest[i] >= 95 > f.highest[i ^ 1]:
                    return i
        if identifier == 'Lowest_Long':
            for i in range(2):
                if f.lowest[i] <= 15 and f.lowest[i ^ 1] <= 15:
                    if f.lowest_long[i] >= 24 and 0 < f.lowest_long[i ^ 1] <= 15:
                        return i
        if identifier == 'Distinct':
            for i in range(2):
                if f.distinct[i] > f.distinct[i^1] == 1:
                    return i^1
        if identifier == 'Integration(>)':
            for i in range(2):
                if predict[i] > predict[i ^ 1]:
                    return i
        if identifier == 'Integration(>1)':
            for i in range(2):
                if predict[i] > predict[i ^ 1] + 1:
                    return i
        if identifier == 'Empty' or 'Integration(empty, >)':
            return -1
        return -1


    iden = identifiers()
    predict = [0, 0]
    for x in range(len(iden.identifier_name)):
        iden.result[x] = calc(f, iden.identifier_name[x])
        if iden.result[x] != -1:
            predict[iden.result[x]] += 1
    return iden
