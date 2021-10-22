from png.png import PNG, png_encode

if __name__ == '__main__':
    W, H = 1000, 1000

    def r_to_b(r, c):
        return r * 128 // H + c * 128 // W, 0, 255 - r * 128 // H - c * 128 // W

    def center(r, c):
        g = 255 - max(abs(r * 2 - H) * 255 // H, abs(c * 2 - W) * 255 // W)
        return g, g, g

    png = PNG(W, H, center, interlace_method=0)
    with open('test.png', 'wb') as f:
        for data in png_encode(png):
            f.write(data)
