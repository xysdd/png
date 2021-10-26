from struct import pack
from png.check import Adler32


def compress(filter_):
    yield b'\x78\x01'
    adler = Adler32()
    deflate = Deflate()
    btype = 1
    for data in filter_:
        deflate.update(data, btype)
        adler.update(data)
    deflate.update(None, btype)
    yield deflate.code(btype)
    yield pack('>L', adler.get())


class Deflate:
    def __init__(self):
        self.buffer = bytearray()
        self.base = 0
        self.pos = 0
        self.npos = 0
        self.blocks = []
        self.symbols = []
        self.wbyte = 0
        self.cur_bit = 0
        self.seqs = {}
        self.match = []
        self.match_len = 0
        self.code_buffer = bytearray()

    def update(self, data, btype=1):
        if btype == 0:
            self.no_compress(data)
        else:
            self.compress(data)

    def no_compress(self, data):
        if data is not None:
            self.buffer += data
        while len(self.buffer) > 65535:
            self.blocks.append((65535, bytes(self.buffer[:65535])))
            self.buffer = self.buffer[65535:]
        if data is None:
            self.blocks.append((len(self.buffer), bytes(self.buffer)))
            self.buffer.clear()

    def compress(self, data):
        if data is not None:
            self.buffer += data
        while self.pos + 2 < len(self.buffer):
            seq = bytes(self.buffer[self.pos:self.pos+3])
            if self.pos >= self.npos:
                if self.match_len > 0:
                    new_match = [p for p in self.match if self.buffer[self.pos] == self.buffer[p + self.match_len - self.base]]
                    if len(new_match) == 0:
                        dist = self.base + self.pos - (self.match[-1] + self.match_len)
                        self.symbols.append((1, (self.match_len, dist)))
                        self.match_len = 0
                    else:
                        self.match_len += 1
                        self.npos += 1
                    self.match = new_match
                    if self.match_len == 258:
                        dist = self.base + self.pos - (self.match[-1] + self.match_len - 1)
                        self.symbols.append((1, (self.match_len, dist)))
                        self.match_len = 0
                        self.match.clear()
                if self.pos >= self.npos:
                    if seq in self.seqs:
                        self.match = [p for p in self.seqs[seq][-16:] if self.base + self.pos - p <= 32768]
                    if len(self.match) == 0:
                        self.symbols.append((0, self.buffer[self.pos]))
                        self.npos += 1
                    else:
                        self.match_len = 3
                        self.npos += 3
            if seq not in self.seqs:
                self.seqs[seq] = []
            self.seqs[seq].append(self.base + self.pos)
            self.pos += 1
        if data is None:
            while self.pos < len(self.buffer):
                if self.pos >= self.npos:
                    if self.match_len > 0:
                        new_match = [p for p in self.match if self.buffer[self.pos] == self.buffer[p + self.match_len - self.base]]
                        if len(new_match) == 0:
                            dist = self.base + self.pos - (self.match[-1] + self.match_len)
                            self.symbols.append((1, (self.match_len, dist)))
                            self.match_len = 0
                        else:
                            self.match_len += 1
                            self.npos += 1
                        self.match = new_match
                        if self.match_len == 258 or self.pos == len(self.buffer) - 1:
                            dist = self.base + self.pos - (self.match[-1] + self.match_len - 1)
                            self.symbols.append((1, (self.match_len, dist)))
                            self.match_len = 0
                            self.match.clear()
                    if self.pos >= self.npos:
                        self.symbols.append((0, self.buffer[self.pos]))
                        self.npos += 1
                self.pos += 1
        if self.pos > 65536:
            self.buffer = self.buffer[self.pos-32768:]
            self.base += self.pos - 32768
            self.npos -= self.pos - 32768
            self.pos = 32768

    def code(self, btype=1):
        if btype == 0:
            for i, (l, d) in enumerate(self.blocks):
                self.write_bits(i == len(self.blocks) - 1, 1, False)
                self.write_bits(btype, 2, False)
                self.fin_byte()
                self.code_buffer += pack('<HH', l, 0xffff ^ l)
                self.code_buffer += d
        elif btype == 1:
            self.write_bits(1, 1, False)
            self.write_bits(btype, 2, False)
            for t, s in self.symbols:
                if t == 0:
                    self.write_bits(*self.fixed_huff(s))
                else:
                    code, extra = self.len_code(s[0])
                    self.write_bits(*self.fixed_huff(code),)
                    self.write_bits(*extra, False)
                    code, extra = self.dist_code(s[1])
                    self.write_bits(code, 5, True)
                    self.write_bits(*extra, False)
            self.write_bits(*self.fixed_huff(256))
            self.fin_byte()
        return bytes(self.code_buffer)

    def fixed_huff(self, lit):
        if lit < 144:
            return 0x30 + lit, 8, True
        elif lit < 256:
            return 0x190 + (lit - 144), 9, True
        elif lit < 280:
            return lit - 256, 7, True
        else:
            return 0xc0 + (lit - 280), 8, True

    def len_code(self, length):
        if length == 258:
            return 285, (0, 0)
        elif length <= 10:
            return 257 + (length - 3), (0, 0)
        else:
            for i in range(1, 6):
                seg = (1 << (i + 2)) + 3
                nseg = (1 << (i + 3)) + 3
                if length < nseg:
                    return 261 + i * 4 + ((length - seg) >> i), ((length - seg) & ((1 << i) - 1), i)

    def dist_code(self, dist):
        if dist <= 4:
            return dist - 1, (0, 0)
        else:
            for i in range(1, 14):
                seg = (1 << (i + 1)) + 1
                nseg = (1 << (i + 2)) + 1
                if dist < nseg:
                    return 2 + i * 2 + ((dist - seg) >> i), ((dist - seg) & ((1 << i) - 1), i)

    def write_bits(self, bits, length, m_to_l):
        r = range(length - 1, -1, -1) if m_to_l else range(length)
        for i in r:
            if self.cur_bit == 8:
                self.code_buffer.append(self.wbyte)
                self.wbyte = 0
                self.cur_bit = 0
            self.wbyte |= ((bits >> i) & 1) << self.cur_bit
            self.cur_bit += 1

    def fin_byte(self):
        if self.cur_bit != 0:
            self.code_buffer.append(self.wbyte)
            self.wbyte = 0
            self.cur_bit = 0
