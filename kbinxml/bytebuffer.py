from struct import *
from typing import Any


class ByteBuffer:
    def __init__(self, input: bytes | bytearray | str = b"", offset=0, endian=">"):
        # so multiple ByteBuffers can hold on to one set of underlying data
        # this is useful for writers in multiple locations
        if isinstance(input, bytearray):
            self.data = input
        else:
            if not isinstance(input, bytes):
                input = input.encode("utf-8")
            self.data = bytearray(input)
        self.endian = endian
        self.offset = offset
        self.end = len(self.data)

    def _format_type(self, type: str, count: int | None = None):
        if count is None:
            return self.endian + type
        else:
            return self.endian + str(count) + type

    def get_bytes(self, count: int):
        start = self.offset
        self.offset += count
        return self.data[start : self.offset]

    def get(self, type: str, count: int | None = None):
        ret = self.peek(type, count)
        size = calcsize(type)
        if count is not None:
            size *= count
        self.offset += size
        return ret

    def peek(self, type: str, count: int | None = None):
        fmt = self._format_type(type, count)
        ret = unpack_from(fmt, self.data, self.offset)
        return ret[0] if count is None else ret

    def append_bytes(self, data: bytes):
        self.data.extend(data)
        self.offset += len(data)

    def append(self, data: Any, type: str, count: int | None = None):
        fmt = self._format_type(type, count)
        self.offset += calcsize(fmt)
        try:
            self.data.extend(pack(fmt, *data))
        except TypeError:
            self.data.extend(pack(fmt, data))

    def set(self, data: Any, offset: int, type: str, count: int | None = None):
        fmt = self._format_type(type, count)
        try:
            pack_into(fmt, self.data, offset, *data)
        except TypeError:
            pack_into(fmt, self.data, offset, data)
        self.offset += calcsize(fmt)

    def hasData(self):
        return self.offset < self.end

    def realign_writes(self, size=4):
        while len(self) % size:
            self.append_u8(0)

    def realign_reads(self, size=4):
        while self.offset % size:
            self.offset += 1

    def __len__(self):
        return len(self.data)

    def get_s8(self) -> int:
        return self.get("b")

    def peek_s8(self) -> int:
        return self.peek("b")

    def append_s8(self, data: int):
        return self.append(data, "b")

    def set_s8(self, data: int, offset: int):
        return self.set(data, offset, "b")

    def get_s16(self) -> int:
        return self.get("h")

    def peek_s16(self) -> int:
        return self.peek("h")

    def append_s16(self, data: int):
        return self.append(data, "h")

    def set_s16(self, data: int, offset: int):
        return self.set(data, offset, "h")

    def get_s32(self) -> int:
        return self.get("i")

    def peek_s32(self) -> int:
        return self.peek("i")

    def append_s32(self, data: int):
        return self.append(data, "i")

    def set_s32(self, data: int, offset: int):
        return self.set(data, offset, "i")

    def get_s64(self) -> int:
        return self.get("q")

    def peek_s64(self) -> int:
        return self.peek("q")

    def append_s64(self, data: int):
        return self.append(data, "q")

    def set_s64(self, data: int, offset: int):
        return self.set(data, offset, "q")

    def get_u8(self) -> int:
        return self.get("B")

    def peek_u8(self) -> int:
        return self.peek("B")

    def append_u8(self, data: int):
        return self.append(data, "B")

    def set_u8(self, data: int, offset: int):
        return self.set(data, offset, "B")

    def get_u16(self) -> int:
        return self.get("H")

    def peek_u16(self) -> int:
        return self.peek("H")

    def append_u16(self, data: int):
        return self.append(data, "H")

    def set_u16(self, data: int, offset: int):
        return self.set(data, offset, "H")

    def get_u32(self) -> int:
        return self.get("I")

    def peek_u32(self) -> int:
        return self.peek("I")

    def append_u32(self, data: int):
        return self.append(data, "I")

    def set_u32(self, data: int, offset: int):
        return self.set(data, offset, "I")

    def get_u64(self) -> int:
        return self.get("Q")

    def peek_u64(self) -> int:
        return self.peek("Q")

    def append_u64(self, data: int):
        return self.append(data, "Q")

    def set_u64(self, data: int, offset: int):
        return self.set(data, offset, "Q")
