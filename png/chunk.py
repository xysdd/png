from struct import pack
from png.check import CRC


def gen_chunk(chunk_type, chunk_data):
    length = len(chunk_data)
    crc = CRC()
    crc.update(chunk_type + chunk_data)
    return pack('>L', length) + chunk_type + chunk_data + pack('>L', crc.get())


def chunk_(compress):
    b = bytearray()
    for data in compress:
        b += data
    yield bytes(b)
