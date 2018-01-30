# python 3 style, ints instead of b''
from builtins import bytes
from bitarray import bitarray

charmap = '0123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz'
bytemap = {charmap[i] : bytes(chr(i).encode()) for i in range(len(charmap))}

def pack_sixbit(string, byteBuf):
    chars = [bytemap[x] for x in string]
    bits = bitarray(endian='big')
    for c in chars:
        bits.frombytes(c)
        # leave only the 6 bits we care for
        del bits[-8:-6]
    data = bytes(bits.tobytes())
    byteBuf.append_bytes((len(string),))
    byteBuf.append_bytes(data)

def unpack_sixbit(byteBuf):
    length = byteBuf.get_u8()
    length_bits = length * 6
    length_bytes = (length_bits + 7) // 8
    bitBuf = bitarray(endian='big')
    bitBuf.frombytes(bytes(byteBuf.get_bytes(length_bytes)))
    result = [bytes(bitBuf[offset:offset+6].tobytes())[0] >> 2
              for offset in range(0, length_bits, 6)]
    return ''.join([charmap[x] for x in result])
