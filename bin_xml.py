from xml.dom import minidom
from struct import calcsize
import string
from bitarray import bitarray
from bytebuffer import ByteBuffer
from format_ids import xml_formats, xml_types

import IPython

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

def pack_bits(string, nodeBuf, bits = 6):
    chars = str_to_sixbit(string)
    bits = bitarray(endian='big')
    for c in chars:
        bits.frombytes(c)
        del bits[-8:-6]
    for c in bits.tobytes():
        nodeBuf.append_u8(ord(c))

def unpack_bits(bitArray, byteBuf, length, bits = 6):
    result = []
    offset = byteBuf.offset * 8
    for i in range(length):
        result.append(ord(bitArray[offset:offset+bits].tobytes()) >> (8 - bits))
        offset += bits
    # padding
    byteBuf.offset += (length * bits + 7) // 8
    return sixbit_to_str(result)

# 0-9 for numbers, 10 to 36 for capitals, 37 for underscore, 38-63 for lowercase
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

def data_grab_auto(dataBuf):
    size = dataBuf.get_s32()
    ret = [dataBuf.get_u8() for x in range(size)]
    # padding
    dataBuf.offset += 3
    # round to dword
    dataBuf.offset &= ~0b11
    return ret

def data_append_auto(dataBuf, data):
    dataBuf.append_s32(len(data))
    dataBuf.append(data, 's', len(data))

    # padding
    while len(dataBuf) % 4:
        dataBuf.append_u8(0)

def data_append_string(dataBuf, string):
    string = string.encode('shift_jisx0213')
    data_append_auto(dataBuf, string)

def data_grab_string(dataBuf):
    data = data_grab_auto(dataBuf)
    res = ''
    for b in data:
        if b == 0:
            break
        res += chr(b)
    return res.decode('shift_jisx0213')

# has its own separate state and other assorted garbage
def data_grab_aligned(dataBuf, dataByteBuf, dataWordBuf, type, count):
    if dataByteBuf.offset % 4 == 0:
        dataByteBuf.offset = dataBuf.offset
    if dataWordBuf.offset % 4 == 0:
        dataWordBuf.offset = dataBuf.offset
    # multiply by count since 2u2 reads from the 16 bit buffer, for example
    size = calcsize(type) * count
    if size == 1:
        ret = dataByteBuf.get(type, count)
    elif size == 2:
        ret = dataWordBuf.get(type, count)
    else:
        ret = dataBuf.get(type, count)
    trailing = max(dataByteBuf.offset, dataWordBuf.offset)
    if dataBuf.offset < trailing:
        dataBuf.offset = trailing + 3
        dataBuf.offset &= ~0b11
    return ret

def is_binary_xml(input):
    nodeBuf = ByteBuffer(input)
    return nodeBuf.get_u16() == SIGNATURE

def _xml_node_to_binary(node, nodeBuf, dataBuf):
    nodeType = node.getAttribute('__type')
    if not nodeType:
        nodeType = 'void'
    nodeId = xml_types[nodeType]

    isArray = 0
    count = node.getAttribute('__count')
    if count:
        count = int(count)
        isArray = 64 # bit position for array flag

    nodeBuf.append_u8(nodeId | isArray)

    name = node.nodeName
    nodeBuf.append_u8(len(name))
    pack_bits(name, nodeBuf)

    import operator
    sorted_x = sorted(node.attributes.items(), key=operator.itemgetter(0))
    for key, value in sorted_x:#node.attributes.items():
        if key in ['__type', '__size', '__count']:
            pass
        else:
            data_append_string(dataBuf, value)
            nodeBuf.append_u8(xml_types['attr'])
            nodeBuf.append_u8(len(key))
            pack_bits(key, nodeBuf)

    if nodeType != 'void':
        nodeId = xml_types[nodeType]
        fmt = xml_formats[nodeId]

        data = map(fmt['pType'], node.firstChild.nodeValue.split(fmt.get('delimiter', ' ')))

        if fmt['count'] == -1 or not isArray:
            data = data[0]
        if isArray or fmt['count'] == -1:
            dataBuf.append_u32(len(data))
            if isArray:
                for d in data:
                    dataBuf.append(d, fmt['type'])
            else:
                dataBuf.append(data, fmt['type'])
        else:
            data_append_aligned(dataBuf, dataByteBuf, dataWordBuf, fmt['type'], fmt['count'])

    for child in node.childNodes:
        if child.nodeType != child.TEXT_NODE:
            _xml_node_to_binary(child, nodeBuf, dataBuf)

    nodeBuf.append_u8(xml_types['nodeEnd'] | 64)

def xml_text_to_binary(input):
    return xml_to_binary(minidom.parseString(input))

def xml_to_binary(input):
    header = ByteBuffer()
    header.append_u16(SIGNATURE)
    header.append_u8(4 << 5) # SHIFT-JIS TODO make encoding variable
    header.append_u8(0x7F) # TODO what does this do as 7f or ff
    nodeBuf = ByteBuffer()
    dataBuf = ByteBuffer()

    for child in input.childNodes:
        _xml_node_to_binary(child, nodeBuf, dataBuf)

    nodeBuf.append_u8(xml_types['endSection'] | 64)
    while len(nodeBuf) % 4 != 0:
        nodeBuf.append_u8(0)
    header.append_u32(len(nodeBuf))
    nodeBuf.append_u32(len(dataBuf))
    return header.data + nodeBuf.data + dataBuf.data

def binary_to_xml_text(input):
    return binary_to_xml(input).toprettyxml(indent="    ", encoding='UTF-8')

def binary_to_xml(input):
    doc = minidom.Document()
    node = doc

    nodeBuf = ByteBuffer(input)
    assert nodeBuf.get_u16() == SIGNATURE
    encoding = encodings[(nodeBuf.get_u8() & 0xE0) >> 5]
    unknown = nodeBuf.get_u8()

    # creating bitarrays is slow, cache for speed
    nodeBits = bitarray(endian='big')
    nodeBits.frombytes(input)

    nodeEnd = nodeBuf.get_u32() + 8
    nodeBuf.end = nodeEnd

    dataBuf = ByteBuffer(input, nodeEnd)
    dataSize = dataBuf.get_u32()
    # WHY MUST YOU DO THIS TO ME
    dataByteBuf = ByteBuffer(input, nodeEnd)
    dataWordBuf = ByteBuffer(input, nodeEnd)

    nodesLeft = True
    while nodesLeft and nodeBuf.hasData():
        while nodeBuf.peek_u8() == 0:
            debug_print("Skipping 0 node ID")
            nodeBuf.get_u8()

        nodeType = nodeBuf.get_u8()
        isArray = nodeType & 64
        nodeType &= ~64

        nodeFormat = xml_formats.get(nodeType, {'name':'Unknown'})
        debug_print('Node type is {} ({})'.format(nodeFormat['name'], nodeType))

        # node name
        name = ''
        if nodeType != xml_types['nodeEnd'] and nodeType != xml_types['endSection']:
            strLen = nodeBuf.get_u8()
            name = unpack_bits(nodeBits, nodeBuf, strLen)
            debug_print(name)

        skip = True

        if nodeType == xml_types['attr']:
            value = data_grab_string(dataBuf)
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

        child = doc.createElement(name)
        node.appendChild(child)
        node = child

        if nodeType == xml_types['nodeStart']:
            continue

        node.setAttribute('__type', nodeFormat['name'])

        if isArray:
            arrayCount = dataBuf.get_u32()
            node.setAttribute('__count', str(arrayCount))
        else:
             arrayCount = 1
        varCount = nodeFormat['count']
        if varCount == -1:
            varCount = dataBuf.get_u32()
        totalCount = arrayCount * varCount

        delim = nodeFormat.get('delimiter', ' ')

        if isArray or nodeFormat['count'] == -1:
            try:
                data = dataBuf.get(nodeFormat['type'], totalCount)
            except:
                print doc.toprettyxml(indent="  ", encoding='UTF-8')
                IPython.embed()
            dataBuf.offset += 3 # padding
            dataBuf.offset &= ~0b11 # align to dword
        else:
            data = data_grab_aligned(dataBuf, dataByteBuf, dataWordBuf, nodeFormat['type'], totalCount)
        string = delim.join(map(str, data))

        if nodeType == xml_types['binary']:
            node.setAttribute('__size', str(totalCount))
            string = ''.join(('{0:02x}'.format(ord(x)) for x in string))
        if nodeType == xml_types['string']:
            string = string[:-1].decode('shift_jisx0213')

        node.appendChild(doc.createTextNode(string))

        #print doc.toprettyxml(indent="  ", encoding='UTF-8')
    return doc


if __name__ == '__main__':
    #input = open('./dump/_core_model=KFC_J_A_A_2016121200_module=package_method=list_out.raw','rb').read()
    #input = open('./dump/KFCmodelKFCJAA2016121200modulegame3methodcommon.raw','rb').read()
    input = open('test.raw', 'rb').read()
    xml = binary_to_xml(input)
    binary = xml_to_binary(xml)
    with open('out.raw', 'wb') as f:
        f.write(binary)

    #print [ord(x) for x in input]
    #print [ord(x) for x in binary]
    #print binary_to_xml_text(input)
    print binary_to_xml_text(binary)
