from struct import pack
from png.chunk import gen_chunk, chunk_
from png.pass_extract import interlace
from png.scanline import scanline
from png.filtering import filter_
from png.compress import compress

signature = b'\x89PNG\r\n\x1a\n'


class PNG:
    def __init__(self, width, height, get_pixel=None, bit_depth=8, colour_type=2, interlace_method=0):
        self.width = width
        self.height = height
        self.get_pixel = get_pixel
        self.bit_depth = bit_depth
        self.colour_type = colour_type
        self.interlace_method = interlace_method
        self.pallete = None


def chunk_ihdr(png):
    header = (png.width, png.height, png.bit_depth, png.colour_type, 0, 0, png.interlace_method)
    ihdr_data = pack('>LLBBBBB', *header)
    return gen_chunk(b'IHDR', ihdr_data)


def chunk_iend():
    return gen_chunk(b'IEND', b'')


def png_encode(png):
    yield signature
    yield chunk_ihdr(png)

    inter = interlace(png, png.interlace_method)
    scan = scanline(png, inter)
    filt = filter_(png, scan)
    comp = compress(filt)
    chunks = chunk_(comp)
    for chunk in chunks:
        yield gen_chunk(b'IDAT', chunk)

    yield chunk_iend()
