from struct import *

class ByteBuffer():
    def __init__(self, input = b'', offset = 0, endian = '>'):
        self.data = input
        self.endian = endian
        self.offset = offset
        self.end = len(self.data)

    def get(self, type, count = None):
        ret = self.peek(type, count)
        size = calcsize(type)
        if count is not None:
            size *= count
        self.offset += size
        return ret

    def peek(self, type, count = None):
        if count is None:
            fmt = self.endian + type
        else:
            fmt = self.endian + str(count) + type
        ret = unpack(fmt, self.data[self.offset:self.offset+calcsize(fmt)])
        return ret[0] if count is None else ret

    def append(self, data, type, count = 1):
        if count is None:
            fmt = self.endian + type
        else:
            fmt = self.endian + str(count) + type
        self.data += pack(fmt, data)

    def hasData(self):
        return self.offset < self.end

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

for name, fmt in typeMap.iteritems():
    _get = _make_get(fmt)
    _peek = _make_peek(fmt)
    _append = _make_append(fmt)
    setattr(ByteBuffer, 'get_' + name, _get)
    setattr(ByteBuffer, 'peek_' + name, _peek)
    setattr(ByteBuffer, 'append_' + name, _append)
