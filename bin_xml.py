from xml.dom import minidom
from struct import calcsize
import string
from bitarray import bitarray
from bytebuffer import ByteBuffer
from format_ids import xml_formats, xml_types
import sys

DEBUG_OFFSETS = False
DEBUG = False

SIGNATURE = 0xA042

encodings = [
    None,
    'ASCII',
    'ISO-8859-1',
    'EUC-JP',
    'SHIFT_JIS',
    'UTF-8'
]

def debug_print(string):
    if DEBUG:
        print string

class kbinxml():

    def __init__(self, input):
        if isinstance(input, minidom.Document):
            self.xml_doc = input
        elif self.is_binary_xml(input):
            self.from_binary(input)
        else:
            self.from_text(input)

    def pack_bits(self, string, bits = 6):
        chars = self.str_to_sixbit(string)
        bits = bitarray(endian='big')
        for c in chars:
            bits.frombytes(c)
            del bits[-8:-6]
        for c in bits.tobytes():
            self.nodeBuf.append_u8(ord(c))

    def unpack_bits(self, length, bits = 6):
        result = []
        offset = self.nodeBuf.offset * 8
        for i in range(length):
            result.append(ord(self.nodeBits[offset:offset+bits].tobytes()) >> (8 - bits))
            offset += bits
        # padding
        self.nodeBuf.offset += (length * bits + 7) // 8
        return self.sixbit_to_str(result)

    # 0-9 for numbers, 10 to 36 for capitals, 37 for underscore, 38-63 for lowercase
    def sixbit_to_str(self, decompressed):
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

    def str_to_sixbit(self, string):
        compress = []
        for c in string:
            if c >= '0' and c <= '9':
                compress.append(ord(c) - ord('0'))
            elif c >= 'A' and c <= 'Z':
                compress.append(ord(c) - 54)
            elif c == '_':
                compress.append(ord(c) - 58)
            elif c >= 'a' and c <= 'z':
                compress.append(ord(c) - 59)
            else:
                raise ValueError('Node name can only contain alphanumeric + underscore')
        return ''.join(map(chr, compress))

    def data_grab_auto(self):
        size = self.dataBuf.get_s32()
        ret = [self.dataBuf.get_u8() for x in range(size)]
        # padding
        self.dataBuf.offset += 3
        # round to dword
        self.dataBuf.offset &= ~0b11
        return ret

    def data_append_auto(self, data):
        self.dataBuf.append_s32(len(data))
        self.dataBuf.append(data, 's', len(data))

        # padding
        while len(self.dataBuf) % 4:
            self.dataBuf.append_u8(0)

    def data_append_string(self, string):
        string = string.encode('shift_jisx0213') + '\0'
        self.data_append_auto(string)

    def data_grab_string(self):
        data = self.data_grab_auto()
        res = ''
        for b in data:
            if b == 0:
                break
            res += chr(b)
        return res.decode('shift_jisx0213')

    # has its own separate state and other assorted garbage
    def data_grab_aligned(self, type, count):
        if self.dataByteBuf.offset % 4 == 0:
            self.dataByteBuf.offset = self.dataBuf.offset
        if self.dataWordBuf.offset % 4 == 0:
            self.dataWordBuf.offset = self.dataBuf.offset
        # multiply by count since 2u2 reads from the 16 bit buffer, for example
        size = calcsize(type) * count
        if size == 1:
            ret = self.dataByteBuf.get(type, count)
        elif size == 2:
            ret = self.dataWordBuf.get(type, count)
        else:
            ret = self.dataBuf.get(type, count)
        trailing = max(self.dataByteBuf.offset, self.dataWordBuf.offset)
        if self.dataBuf.offset < trailing:
            self.dataBuf.offset = trailing + 3
            self.dataBuf.offset &= ~0b11
        return ret

    def data_append_aligned(self, data, type, count):
        if self.dataByteBuf.offset % 4 == 0:
            self.dataByteBuf.offset = self.dataBuf.offset
        if self.dataWordBuf.offset % 4 == 0:
            self.dataWordBuf.offset = self.dataBuf.offset
        # multiply by count since 2u2 reads from the 16 bit buffer, for example
        size = calcsize(type) * count
        if size == 1:
            # make room if fresh dword for our stuff
            if self.dataByteBuf.offset % 4 == 0:
                self.dataBuf.append_u32(0)
            self.dataByteBuf.set(data, self.dataByteBuf.offset, type, count)
        elif size == 2:
            if self.dataWordBuf.offset % 4 == 0:
                self.dataBuf.append_u32(0)
            self.dataWordBuf.set(data, self.dataWordBuf.offset, type, count)
        else:
            self.dataBuf.append(data, type, count)

    def is_binary_xml(self, input):
        nodeBuf = ByteBuffer(input)
        return nodeBuf.get_u16() == SIGNATURE

    def _node_to_binary(self, node):
        nodeType = node.getAttribute('__type')
        if not nodeType:
            nodeType = 'void'
        nodeId = xml_types[nodeType]

        isArray = 0
        count = node.getAttribute('__count')
        if count:
            count = int(count)
            isArray = 64 # bit position for array flag

        self.nodeBuf.append_u8(nodeId | isArray)

        name = node.nodeName
        self.nodeBuf.append_u8(len(name))
        self.pack_bits(name)

        if nodeType != 'void':
            fmt = xml_formats[nodeId]

            val = node.firstChild.nodeValue
            if fmt['count'] != -1:
                val = val.split(fmt.get('delimiter', ' '))
                data = map(fmt['pType'], val)
            else:
                data = fmt['pType'](val)

            if isArray or fmt['count'] == -1:
                self.dataBuf.append_u32(len(data) * calcsize(fmt['type']))
                self.dataBuf.append(data, fmt['type'], len(data))
                # padding
                while len(self.dataBuf) % 4:
                    self.dataBuf.append_u8(0)
            else:
                self.data_append_aligned(data, fmt['type'], fmt['count'])

        import operator
        sorted_x = sorted(node.attributes.items(), key=operator.itemgetter(0))
        for key, value in sorted_x:#node.attributes.items():
            if key in ['__type', '__size', '__count']:
                pass
            else:
                self.data_append_string(value)
                self.nodeBuf.append_u8(xml_types['attr'])
                self.nodeBuf.append_u8(len(key))
                self.pack_bits(key)
                
        for child in node.childNodes:
            if child.nodeType != child.TEXT_NODE:
                self._node_to_binary(child)

        self.nodeBuf.append_u8(xml_types['nodeEnd'] | 64)

    def from_text(self, input):
        self.xml_doc = minidom.parseString(input)

    def to_binary(self):
        header = ByteBuffer()
        header.append_u16(SIGNATURE)
        header.append_u8(4 << 5) # SHIFT-JIS TODO make encoding variable
        header.append_u8(0x7F) # TODO what does this do as 7f or ff
        self.nodeBuf = ByteBuffer()
        self.dataBuf = ByteBuffer()
        self.dataByteBuf = ByteBuffer(self.dataBuf.data)
        self.dataWordBuf = ByteBuffer(self.dataBuf.data)

        for child in self.xml_doc.childNodes:
            self._node_to_binary(child)

        self.nodeBuf.append_u8(xml_types['endSection'] | 64)
        while len(self.nodeBuf) % 4 != 0:
            self.nodeBuf.append_u8(0)
        header.append_u32(len(self.nodeBuf))
        self.nodeBuf.append_u32(len(self.dataBuf))
        return bytes(header.data + self.nodeBuf.data + self.dataBuf.data)

    def to_text(self):
        return self.xml_doc.toprettyxml(indent="    ", encoding='UTF-8')

    def from_binary(self, input):
        self.xml_doc = minidom.Document()
        node = self.xml_doc

        self.nodeBuf = ByteBuffer(input)
        assert self.nodeBuf.get_u16() == SIGNATURE
        encoding = encodings[(self.nodeBuf.get_u8() & 0xE0) >> 5]
        unknown = self.nodeBuf.get_u8()

        # creating bitarrays is slow, cache for speed
        self.nodeBits = bitarray(endian='big')
        self.nodeBits.frombytes(input)

        nodeEnd = self.nodeBuf.get_u32() + 8
        self.nodeBuf.end = nodeEnd

        self.dataBuf = ByteBuffer(input, nodeEnd)
        dataSize = self.dataBuf.get_u32()
        # WHY MUST YOU DO THIS TO ME
        self.dataByteBuf = ByteBuffer(input, nodeEnd)
        self.dataWordBuf = ByteBuffer(input, nodeEnd)

        nodesLeft = True
        while nodesLeft and self.nodeBuf.hasData():
            while self.nodeBuf.peek_u8() == 0:
                debug_print("Skipping 0 node ID")
                self.nodeBuf.get_u8()

            nodeType = self.nodeBuf.get_u8()
            isArray = nodeType & 64
            nodeType &= ~64

            nodeFormat = xml_formats.get(nodeType, {'name':'Unknown'})
            debug_print('Node type is {} ({})'.format(nodeFormat['name'], nodeType))

            # node name
            name = ''
            if nodeType != xml_types['nodeEnd'] and nodeType != xml_types['endSection']:
                strLen = self.nodeBuf.get_u8()
                name = self.unpack_bits(strLen)
                debug_print(name)

            skip = True

            if nodeType == xml_types['attr']:
                value = self.data_grab_string()
                node.setAttribute(name, value)
            elif nodeType == xml_types['nodeEnd']:
                if node.parentNode:
                    node = node.parentNode
            elif nodeType == xml_types['endSection']:
                nodesLeft = False
            elif nodeType not in xml_formats:
                raise NotImplementedError('Implement node {}'.format(nodeType))
            else: # inner value to process
                skip = False

            if skip:
                continue

            child = self.xml_doc.createElement(name)
            node.appendChild(child)
            node = child

            if nodeType == xml_types['nodeStart']:
                continue

            node.setAttribute('__type', nodeFormat['name'])

            if isArray:
                arrayCount = self.dataBuf.get_u32() / calcsize(nodeFormat['type'])
                node.setAttribute('__count', str(arrayCount))
            else:
                 arrayCount = 1
            varCount = nodeFormat['count']
            if varCount == -1:
                varCount = self.dataBuf.get_u32()
            totalCount = arrayCount * varCount

            delim = nodeFormat.get('delimiter', ' ')

            if isArray or nodeFormat['count'] == -1:
                data = self.dataBuf.get(nodeFormat['type'], totalCount)
                self.dataBuf.offset += 3 # padding
                self.dataBuf.offset &= ~0b11 # align to dword
            else:
                data = self.data_grab_aligned(nodeFormat['type'], totalCount)
            string = delim.join(map(str, data))

            if nodeType == xml_types['binary']:
                node.setAttribute('__size', str(totalCount))
                string = ''.join(('{0:02x}'.format(ord(x)) for x in string))
            if nodeType == xml_types['string']:
                string = string[:-1].decode('shift_jisx0213')

            node.appendChild(self.xml_doc.createTextNode(string))

            #print self.xml_doc.toprettyxml(indent="  ", encoding='UTF-8')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'bin_xml.py file1 [file2 ...]'

    # by default, confirm the implementation is correct
    for f in sys.argv[1:]:
        with open(f, 'rb') as f:
            input = f.read()
        xml = kbinxml(input)
        print xml.to_text()
        try:
            # just politely ignore the signature since we don't do encoding yet
            assert xml.to_binary()[4:] == input[4:]
        except AssertionError:
            print 'Files do not match!'
            with open('out.raw', 'wb') as f:
                f.write(xml.to_binary())
