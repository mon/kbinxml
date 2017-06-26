# python 3 style, ints instead of b''
from builtins import bytes
from xml.dom import minidom
from struct import calcsize
import string
import sys
import operator

from bytebuffer import ByteBuffer
from sixbit import pack_sixbit, unpack_sixbit
from format_ids import xml_formats, xml_types

stdout = getattr(sys.stdout, 'buffer', sys.stdout)

DEBUG_OFFSETS = False
DEBUG = False

SIGNATURE = 0xA0

SIG_COMPRESSED = 0x42
SIG_UNCOMPRESSED = 0x45

XML_ENCODING = 'UTF_8'
BIN_ENCODING = 'SHIFT_JISX0213'

# NOTE: all of these are their python codec names
encoding_strings = {
    0x20: 'ASCII',
    0x00: 'ISO-8859-1',
    0x60: 'EUC_JP',
    0x80: 'SHIFT_JISX0213',
    0xA0: 'UTF_8'
}

encoding_vals = {val : key for key, val in encoding_strings.items()}

def debug_print(string):
    if DEBUG:
        print(string)

class KBinXML():

    def __init__(self, input):
        if isinstance(input, minidom.Document):
            self.xml_doc = input
        elif KBinXML.is_binary_xml(input):
            self.from_binary(input)
        else:
            self.from_text(input)

    def to_text(self):
        return self.xml_doc.toprettyxml(indent = "    ", encoding = XML_ENCODING)

    def from_text(self, input):
        self.xml_doc = minidom.parseString(input)

    @staticmethod
    def is_binary_xml(input):
        nodeBuf = ByteBuffer(input)
        return (nodeBuf.get_u8() == SIGNATURE and
            nodeBuf.get_u8() in (SIG_COMPRESSED, SIG_UNCOMPRESSED))

    def data_grab_auto(self):
        size = self.dataBuf.get_s32()
        ret = self.dataBuf.get('b', size)
        self.dataBuf.realign_reads()
        return ret

    def data_append_auto(self, data):
        self.dataBuf.append_s32(len(data))
        self.dataBuf.append(data, 'b', len(data))
        self.dataBuf.realign_writes()

    def data_grab_string(self):
        data = self.data_grab_auto()
        return bytes(data[:-1]).decode(self.encoding)

    def data_append_string(self, string):
        string = bytes(string.encode(self.encoding) + b'\0')
        self.data_append_auto(string)

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
            self.dataBuf.realign_reads()
        trailing = max(self.dataByteBuf.offset, self.dataWordBuf.offset)
        if self.dataBuf.offset < trailing:
            self.dataBuf.offset = trailing
            self.dataBuf.realign_reads()
        return ret

    def data_append_aligned(self, data, type, count):
        if self.dataByteBuf.offset % 4 == 0:
            self.dataByteBuf.offset = self.dataBuf.offset
        if self.dataWordBuf.offset % 4 == 0:
            self.dataWordBuf.offset = self.dataBuf.offset
        # multiply by count since 2u2 reads from the 16 bit buffer, for example
        size = calcsize(type) * count
        if size == 1:
            # make room for our stuff if fresh dword
            if self.dataByteBuf.offset % 4 == 0:
                self.dataBuf.append_u32(0)
            self.dataByteBuf.set(data, self.dataByteBuf.offset, type, count)
        elif size == 2:
            if self.dataWordBuf.offset % 4 == 0:
                self.dataBuf.append_u32(0)
            self.dataWordBuf.set(data, self.dataWordBuf.offset, type, count)
        else:
            self.dataBuf.append(data, type, count)
            self.dataBuf.realign_writes()

    def _node_to_binary(self, node):
        if node.nodeType == node.TEXT_NODE or node.nodeType == node.COMMENT_NODE:
            return
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
        pack_sixbit(name, self.nodeBuf)

        if nodeType != 'void':
            fmt = xml_formats[nodeId]

            val = node.firstChild.nodeValue
            if fmt['name'] == 'bin':
                data = bytes(bytearray.fromhex(val))
            elif fmt['name'] == 'str':
                data = bytes(val.encode(self.encoding) + b'\0')
            else:
                val = val.split(' ')
                data = list(map(fmt.get('fromStr', int), val))
                if count and len(data) / fmt['count'] != count:
                    raise ValueError('Array length does not match __count attribute')

            if isArray or fmt['count'] == -1:
                self.dataBuf.append_u32(len(data) * calcsize(fmt['type']))
                self.dataBuf.append(data, fmt['type'], len(data))
                self.dataBuf.realign_writes()
            else:
                self.data_append_aligned(data, fmt['type'], fmt['count'])

        # for test consistency and to be more faithful, sort the attrs
        sorted_attrs = sorted(node.attributes.items(), key=operator.itemgetter(0))
        for key, value in sorted_attrs:
            if key not in ['__type', '__size', '__count']:
                self.data_append_string(value)
                self.nodeBuf.append_u8(xml_types['attr'])
                pack_sixbit(key, self.nodeBuf)

        for child in node.childNodes:
            self._node_to_binary(child)

        # always has the isArray bit set
        self.nodeBuf.append_u8(xml_types['nodeEnd'] | 64)

    def to_binary(self):
        self.encoding = BIN_ENCODING

        header = ByteBuffer()
        header.append_u8(SIGNATURE)
        header.append_u8(SIG_COMPRESSED)
        header.append_u8(encoding_vals[self.encoding])
        # Python's ints are big, so can't just bitwise invert
        header.append_u8(0xFF ^ encoding_vals[self.encoding])
        self.nodeBuf = ByteBuffer()
        self.dataBuf = ByteBuffer()
        self.dataByteBuf = ByteBuffer(self.dataBuf.data)
        self.dataWordBuf = ByteBuffer(self.dataBuf.data)

        for child in self.xml_doc.childNodes:
            self._node_to_binary(child)

        # always has the isArray bit set
        self.nodeBuf.append_u8(xml_types['endSection'] | 64)
        self.nodeBuf.realign_writes()
        header.append_u32(len(self.nodeBuf))
        self.nodeBuf.append_u32(len(self.dataBuf))
        return bytes(header.data + self.nodeBuf.data + self.dataBuf.data)

    def from_binary(self, input):
        self.xml_doc = minidom.Document()
        node = self.xml_doc

        self.nodeBuf = ByteBuffer(input)
        assert self.nodeBuf.get_u8() == SIGNATURE

        compress = self.nodeBuf.get_u8()
        assert compress in (SIG_COMPRESSED, SIG_UNCOMPRESSED)
        self.compressed = compress == SIG_COMPRESSED

        encoding_key = self.nodeBuf.get_u8()
        assert self.nodeBuf.get_u8() == 0xFF ^ encoding_key
        self.encoding = encoding_strings[encoding_key]

        nodeEnd = self.nodeBuf.get_u32() + 8
        self.nodeBuf.end = nodeEnd

        self.dataBuf = ByteBuffer(input, nodeEnd)
        dataSize = self.dataBuf.get_u32()
        # This is all no fun
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

            # node or attribute name
            name = ''
            if nodeType != xml_types['nodeEnd'] and nodeType != xml_types['endSection']:
                if self.compressed:
                    name = unpack_sixbit(self.nodeBuf)
                else:
                    length = self.nodeBuf.get_u8()
                    name = self.nodeBuf.get('s', length)
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

            varCount = nodeFormat['count']
            arrayCount = 1
            if varCount == -1: # the 2 cannot be combined
                varCount = self.dataBuf.get_u32()
                isArray = True
            elif isArray:
                arrayCount = self.dataBuf.get_u32() // (calcsize(nodeFormat['type'] * varCount))
                node.setAttribute('__count', str(arrayCount))
            totalCount = arrayCount * varCount

            if isArray:
                data = self.dataBuf.get(nodeFormat['type'], totalCount)
                self.dataBuf.realign_reads()
            else:
                data = self.data_grab_aligned(nodeFormat['type'], totalCount)

            if nodeType == xml_types['binary']:
                node.setAttribute('__size', str(totalCount))
                string = ''.join(('{0:02x}'.format(x) for x in data))
            elif nodeType == xml_types['string']:
                string = bytes(data[:-1]).decode(self.encoding)
            else:
                string = ' '.join(map(nodeFormat.get('toStr', str), data))

            node.appendChild(self.xml_doc.createTextNode(string))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('bin_xml.py file.[xml/bin]')
        exit()

    with open(sys.argv[1], 'rb') as f:
        input = f.read()

    xml = KBinXML(input)
    if KBinXML.is_binary_xml(input):
        stdout.write(xml.to_text())
    else:
        stdout.write(xml.to_binary())
