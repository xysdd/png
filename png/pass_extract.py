def interlace(png, method=0):
    return method_dict[method](png)


def null(png):
    for r in range(png.height):
        yield 0, [(r, c) for c in range(png.width)]
    yield 1,


def adam7(png):
    r0 = [0, 0, 4, 0, 2, 0, 1]
    c0 = [0, 4, 0, 2, 0, 1, 0]
    dr = [8, 8, 8, 4, 4, 2, 2]
    dc = [8, 8, 4, 4, 2, 2, 1]
    for p in range(7):
        for r in range(r0[p], png.height, dr[p]):
            yield 0, [(r, c) for c in range(c0[p], png.width, dc[p])]
        yield 1,


method_dict = {
    0: null,
    1: adam7,
}
