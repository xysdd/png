from struct import pack


def scanline(png, interlace):
    b = bytearray()
    for d in interlace:
        if d[0] == 0:
            for r, c in d[1]:
                pixel = png.get_pixel(r, c)[:png.nsample]
                b += bytes(pixel)
            yield 0, bytes(b)
            b.clear()
        elif d[0] == 1:
            yield 1,
