class Adler32:
    def __init__(self):
        self.a = 1
        self.b = 0

    def update(self, data):
        for byte in data:
            self.a = (self.a + byte) % 65521
            self.b = (self.b + self.a) % 65521

    def get(self):
        return (self.b << 16) + self.a


def init_crc_table():
    for i in range(256):
        c = i
        for k in range(8):
            if c & 1:
                c = 0xedb88320 ^ (c >> 1)
            else:
                c = c >> 1
        crc_table.append(c)


class CRC:
    def __init__(self):
        self.c = 0xffffffff

    def update(self, data):
        for b in data:
            self.c = crc_table[(self.c ^ b) & 0xff] ^ (self.c >> 8)

    def get(self):
        return self.c ^ 0xffffffff


crc_table = []
init_crc_table()
