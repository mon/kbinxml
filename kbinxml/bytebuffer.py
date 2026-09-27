from functools import lru_cache
from struct import *
from typing import Any


@lru_cache(maxsize=None)
def _struct(fmt: str) -> Struct:
    return Struct(fmt)


class ByteBuffer:
    def __init__(self, input: bytes | bytearray | str = b"", offset=0, endian=">"):
        # so multiple ByteBuffers can hold on to one set of underlying data
        # this is useful for writers in multiple locations
        if isinstance(input, bytearray):
            self.data = input
        elif isinstance(input, bytes):
            # empty bytes -> writable buffer for writers; non-empty -> view for readers
            self.data = bytearray() if not input else memoryview(input)
        else:
            self.data = memoryview(input.encode("utf-8"))
        self.endian = endian
        self.offset = offset
        self.end = len(self.data)

        self._s8 = _struct(endian + "b")
        self._u8 = _struct(endian + "B")
        self._s16 = _struct(endian + "h")
        self._u16 = _struct(endian + "H")
        self._s32 = _struct(endian + "i")
        self._u32 = _struct(endian + "I")
        self._s64 = _struct(endian + "q")
        self._u64 = _struct(endian + "Q")

    def _format_type(self, type: str, count: int | None = None):
        if count is None:
            return self.endian + type
        else:
            return self.endian + str(count) + type

    def get_bytes(self, count: int):
        start = self.offset
        self.offset += count
        return self.data[start : self.offset]

    def get_bytes_exact(self, count: int):
        ret = self.get_bytes(count)
        if len(ret) != count:
            raise error(
                f"unpack_from requires a buffer of at least {self.offset} bytes"
            )
        return ret

    def get(self, type: str, count: int | None = None):
        s = _struct(self._format_type(type, count))
        ret = s.unpack_from(self.data, self.offset)
        self.offset += s.size
        return ret[0] if count is None else ret

    def peek(self, type: str, count: int | None = None):
        ret = _struct(self._format_type(type, count)).unpack_from(
            self.data, self.offset
        )
        return ret[0] if count is None else ret

    def append_bytes(self, data: bytes):
        self.data.extend(data)
        self.offset += len(data)

    def append(self, data: Any, type: str, count: int | None = None):
        s = _struct(self._format_type(type, count))
        self.offset += s.size
        try:
            self.data.extend(s.pack(*data))
        except TypeError:
            self.data.extend(s.pack(data))

    def set(self, data: Any, offset: int, type: str, count: int | None = None):
        s = _struct(self._format_type(type, count))
        try:
            s.pack_into(self.data, offset, *data)
        except TypeError:
            s.pack_into(self.data, offset, data)
        self.offset += s.size

    def hasData(self):
        return self.offset < self.end

    def realign_writes(self, size=4):
        pad = (-len(self.data)) % size
        if pad:
            self.data.extend(b"\0" * pad)
            self.offset += pad

    def realign_reads(self, size=4):
        rem = self.offset % size
        if rem:
            self.offset += size - rem

    def __len__(self):
        return len(self.data)

    def _get_fixed(self, s: Struct) -> int:
        ret = s.unpack_from(self.data, self.offset)[0]
        self.offset += s.size
        return ret

    def _peek_fixed(self, s: Struct) -> int:
        return s.unpack_from(self.data, self.offset)[0]

    def _append_fixed(self, s: Struct, data: int):
        self.data.extend(s.pack(data))
        self.offset += s.size

    def _set_fixed(self, s: Struct, data: int, offset: int):
        s.pack_into(self.data, offset, data)
        self.offset += s.size

    def get_s8(self) -> int:
        return self._get_fixed(self._s8)

    def peek_s8(self) -> int:
        return self._peek_fixed(self._s8)

    def append_s8(self, data: int):
        return self._append_fixed(self._s8, data)

    def set_s8(self, data: int, offset: int):
        return self._set_fixed(self._s8, data, offset)

    def get_s16(self) -> int:
        return self._get_fixed(self._s16)

    def peek_s16(self) -> int:
        return self._peek_fixed(self._s16)

    def append_s16(self, data: int):
        return self._append_fixed(self._s16, data)

    def set_s16(self, data: int, offset: int):
        return self._set_fixed(self._s16, data, offset)

    def get_s32(self) -> int:
        return self._get_fixed(self._s32)

    def peek_s32(self) -> int:
        return self._peek_fixed(self._s32)

    def append_s32(self, data: int):
        return self._append_fixed(self._s32, data)

    def set_s32(self, data: int, offset: int):
        return self._set_fixed(self._s32, data, offset)

    def get_s64(self) -> int:
        return self._get_fixed(self._s64)

    def peek_s64(self) -> int:
        return self._peek_fixed(self._s64)

    def append_s64(self, data: int):
        return self._append_fixed(self._s64, data)

    def set_s64(self, data: int, offset: int):
        return self._set_fixed(self._s64, data, offset)

    def get_u8(self) -> int:
        return self._get_fixed(self._u8)

    def peek_u8(self) -> int:
        return self._peek_fixed(self._u8)

    def append_u8(self, data: int):
        return self._append_fixed(self._u8, data)

    def set_u8(self, data: int, offset: int):
        return self._set_fixed(self._u8, data, offset)

    def get_u16(self) -> int:
        return self._get_fixed(self._u16)

    def peek_u16(self) -> int:
        return self._peek_fixed(self._u16)

    def append_u16(self, data: int):
        return self._append_fixed(self._u16, data)

    def set_u16(self, data: int, offset: int):
        return self._set_fixed(self._u16, data, offset)

    def get_u32(self) -> int:
        return self._get_fixed(self._u32)

    def peek_u32(self) -> int:
        return self._peek_fixed(self._u32)

    def append_u32(self, data: int):
        return self._append_fixed(self._u32, data)

    def set_u32(self, data: int, offset: int):
        return self._set_fixed(self._u32, data, offset)

    def get_u64(self) -> int:
        return self._get_fixed(self._u64)

    def peek_u64(self) -> int:
        return self._peek_fixed(self._u64)

    def append_u64(self, data: int):
        return self._append_fixed(self._u64, data)

    def set_u64(self, data: int, offset: int):
        return self._set_fixed(self._u64, data, offset)
