from kbinxml.bytebuffer import ByteBuffer


charmap = "0123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
bytemap = {c: i for i, c in enumerate(charmap)}


def pack_sixbit(string: str, byteBuf: ByteBuffer):
    chars = [bytemap[x] for x in string]
    padding = 8 - (len(string) * 6 % 8)
    if padding == 8:
        padding = 0
    bits = 0
    for c in chars:
        bits <<= 6
        bits |= c
    bits <<= padding
    data = bits.to_bytes((len(string) * 6 + padding) // 8, byteorder="big")
    byteBuf.append_bytes((len(string),))
    byteBuf.append_bytes(data)


def unpack_sixbit(byteBuf: ByteBuffer):
    length = byteBuf.get_u8()
    length_bits = length * 6
    length_bytes = (length_bits + 7) // 8
    padding = 8 - (length_bits % 8)
    if padding == 8:
        padding = 0
    bits = int.from_bytes(byteBuf.get_bytes(length_bytes), byteorder="big")
    bits >>= padding
    result = []
    for _ in range(length):
        result.append(bits & 0b111111)
        bits >>= 6
    return "".join([charmap[x] for x in result[::-1]])
