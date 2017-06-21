from bitarray import bitarray

def pack_sixbit(string, byteBuf):
    chars = str_to_sixbit(string)
    bits = bitarray(endian='big')
    for c in chars:
        bits.frombytes(c)
        # leave only the 6 bits we care for
        del bits[-8:-6]
    data = bits.tobytes()
    byteBuf.append_u8(len(string))
    byteBuf.append(data, 'c', len(data))

def unpack_sixbit(byteBuf):
    bitBuf = bitarray(endian='big')
    bitBuf.frombytes(bytes(byteBuf.data))
    length = byteBuf.get_u8()
    result = []
    offset = byteBuf.offset * 8
    for i in range(length):
        result.append(ord(bitBuf[offset:offset+6].tobytes()) >> (8 - 6))
        offset += 6
    # padding
    byteBuf.offset += (length * 6 + 7) // 8
    return sixbit_to_str(result)

# 0-9 for numbers, 10 is ':', 11 to 36 for capitals, 37 for underscore, 38-63 for lowercase
def sixbit_to_str(decompressed):
    string = ''
    for d in decompressed:
        if d <= 10:
            d += ord('0')
        elif d < 37:
            d += 54
        elif d == 37:
            d += 58
        else:
            d += 59
        string += chr(d)
    return string

def str_to_sixbit(string):
    compress = []
    for c in string:
        if c >= '0' and c <= ':':
            compress.append(ord(c) - ord('0'))
        elif c >= 'A' and c <= 'Z':
            compress.append(ord(c) - 54)
        elif c == '_':
            compress.append(ord(c) - 58)
        elif c >= 'a' and c <= 'z':
            compress.append(ord(c) - 59)
        else:
            raise ValueError('Node or attribute name can only contain alphanumeric + underscore')
    return ''.join(map(chr, compress))
