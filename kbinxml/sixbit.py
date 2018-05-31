# python 3 style, ints instead of b''
from builtins import bytes as newbytes

def py2_int_to_bytes(n, length):
    h = '%x' % n
    s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
    return newbytes(s)

try:
    # python 3
    int.from_bytes
    int_from_bytes = lambda b : int.from_bytes(b, byteorder='big')
    int_to_bytes = lambda i, length : i.to_bytes(length, byteorder='big')
except AttributeError:
    # python 2
    int_from_bytes = lambda b : int(bytes(b).encode('hex'), 16)
    int_to_bytes = py2_int_to_bytes


charmap = '0123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
bytemap = {charmap[i] : i for i in range(len(charmap))}

def pack_sixbit(string, byteBuf):
    chars = [bytemap[x] for x in string]
    padding = 8 - (len(string)*6 % 8)
    if padding == 8:
        padding = 0
    bits = 0
    for c in chars:
        bits <<= 6
        bits |= c
    bits <<= padding
    data = int_to_bytes(bits, (len(string)*6 + padding) // 8)
    byteBuf.append_bytes((len(string),))
    byteBuf.append_bytes(data)

def unpack_sixbit(byteBuf):
    length = byteBuf.get_u8()
    length_bits = length * 6
    length_bytes = (length_bits + 7) // 8
    padding = 8 - (length_bits % 8)
    if padding == 8:
        padding = 0
    bits = int_from_bytes(byteBuf.get_bytes(length_bytes))
    bits >>= padding
    result = []
    for _ in range(length):
        result.append(bits & 0b111111)
        bits >>= 6
    return ''.join([charmap[x] for x in result[::-1]])
