EDGE_MM = 116
CONST = False
PIXELS = 128


def data_to_edge(data):
    n = int(data[0])
    edge = [0 for i in range(PIXELS) * 2]
    p = 1
    for touch in range(n):
        bar = int(data[p])
        force = int(data[p+2])
        pos0 = float(data[p+4])
        pos1 = float(data[p+5])
        if force == 0:
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
    return n, edge

