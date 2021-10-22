from struct import pack
from png.check import Adler32


def compress(filter_):
    yield b'\x78\x01'
    b = bytearray()
    adler = Adler32()
    for data in filter_:
        b += data
        adler.update(data)
    yield deflate(b)
    yield pack('>L', adler.get())


def deflate(data):
    blocks = []
    for i in range(0, len(data), 65535):
        b = data[i:i+65535]
        if i < len(data) - 65535:
            blocks.append(b'\x00' + pack('<HH', len(b), 0xffff ^ len(b)) + b)
        else:
            blocks.append(b'\x01' + pack('<HH', len(b), 0xffff ^ len(b)) + b)
    return b''.join(blocks)
