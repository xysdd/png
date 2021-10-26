def filter_(png, scanline):
    last_line = None
    for d in scanline:
        if d[0] == 0:
            line = d[1]
            filt_lines = []
            sa = []
            for t in range(5):
                fl, s = filt_list[t](line, last_line, png.bit_depth // 8 * png.nsample)
                filt_lines.append(fl)
                sa.append(s)
            ts = sa.index(min(sa))
            yield bytes([ts]) + filt_lines[ts]
            last_line = line
        elif d[0] == 1:
            last_line = None


def filt_none(line, last_line, pixel_size):
    return line, sum(line)


def filt_sub(line, last_line, pixel_size):
    f = [line[i] - (line[i - pixel_size] if i >= pixel_size else 0) for i in range(len(line))]
    filt_line = bytes(b % 256 for b in f)
    sa = sum(abs(b) for b in f)
    return filt_line, sa


def filt_up(line, last_line, pixel_size):
    if last_line is None:
        last_line = bytes(len(line))
    f = [line[i] - last_line[i] for i in range(len(line))]
    filt_line = bytes(b % 256 for b in f)
    sa = sum(abs(b) for b in f)
    return filt_line, sa


def filt_average(line, last_line, pixel_size):
    if last_line is None:
        last_line = bytes(len(line))
    f = [line[i] - ((line[i - pixel_size] if i >= pixel_size else 0) + last_line[i]) // 2 for i in range(len(line))]
    filt_line = bytes(b % 256 for b in f)
    sa = sum(abs(b) for b in f)
    return filt_line, sa


def filt_paeth(line, last_line, pixel_size):
    if last_line is None:
        last_line = bytes(len(line))
    f = [line[i] - paeth_predictor((line[i - pixel_size] if i >= pixel_size else 0), last_line[i], (last_line[i - pixel_size] if i >= pixel_size else 0)) for i in range(len(line))]
    filt_line = bytes(b % 256 for b in f)
    sa = sum(abs(b) for b in f)
    return filt_line, sa


def paeth_predictor(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        pr = a
    elif pb <= pc:
        pr = b
    else:
        pr = c
    return pr


filt_list = [filt_none, filt_sub, filt_up, filt_average, filt_paeth]