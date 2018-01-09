from struct import *

class ByteBuffer():
    def __init__(self, input = b'', offset = 0, endian = '>'):
        # so multiple ByteBuffers can hold on to one set of underlying data
        # this is useful for writers in multiple locations
        if isinstance(input, bytearray):
            self.data = input
        else:
            if not isinstance(input, bytes):
                input = input.encode('utf-8')
            self.data = bytearray(input)
        self.endian = endian
        self.offset = offset
        self.end = len(self.data)

    def _format_type(self, type, count):
        if count is None:
            return self.endian + type
        else:
            return self.endian + str(count) + type

    def get_bytes(self, count):
        start = self.offset
        self.offset += count
        return self.data[start:self.offset]

    def get(self, type, count = None):
        ret = self.peek(type, count)
        size = calcsize(type)
        if count is not None:
            size *= count
        self.offset += size
        return ret

    def peek(self, type, count = None):
        fmt = self._format_type(type, count)
        ret = unpack_from(fmt, self.data, self.offset)
        return ret[0] if count is None else ret

    def append_bytes(self, data):
        self.data.extend(data)
        self.offset += len(data)

    def append(self, data, type, count = None):
        fmt = self._format_type(type, count)
        self.offset += calcsize(fmt)
        try:
            self.data.extend(pack(fmt, *data))
        except TypeError:
            self.data.extend(pack(fmt, data))

    def set(self, data, offset, type, count = None):
        fmt = self._format_type(type, count)
        try:
            pack_into(fmt, self.data, offset, *data)
        except TypeError:
            pack_into(fmt, self.data, offset, data)
        self.offset += calcsize(fmt)

    def hasData(self):
        return self.offset < self.end

    def realign_writes(self, size = 4):
        while len(self) % size:
            self.append_u8(0)

    def realign_reads(self, size = 4):
        while self.offset % size:
            self.offset += 1

    def __len__(self):
        return len(self.data)

typeMap = {
    's8'  : 'b',
    's16' : 'h',
    's32' : 'i',
    's64' : 'q',
    'u8'  : 'B',
    'u16' : 'H',
    'u32' : 'I',
    'u64' : 'Q'
}

def _make_get(fmt):
    def _method(self):
        return self.get(fmt)
    return _method

def _make_peek(fmt):
    def _method(self):
        return self.peek(fmt)
    return _method

def _make_append(fmt):
    def _method(self, data):
        return self.append(data, fmt)
    return _method

def _make_set(fmt):
    def _method(self, data, offset):
        return self.set(data, offset, fmt)
    return _method

for name, fmt in typeMap.items():
    _get = _make_get(fmt)
    _peek = _make_peek(fmt)
    _append = _make_append(fmt)
    _set = _make_set(fmt)
    setattr(ByteBuffer, 'get_' + name, _get)
    setattr(ByteBuffer, 'peek_' + name, _peek)
    setattr(ByteBuffer, 'append_' + name, _append)
    setattr(ByteBuffer, 'set_' + name, _set)
