from struct import pack, unpack

def parseIP(string):
    bunch = map(int, string.split('.'))
    # pack to bytes
    p = pack('4B', *bunch)
    # unpack as u16
    return unpack('>I', p)[0]

def writeIP(raw):
    # pack to bytes
    p = pack('>I', raw)
    # unpack
    return '.'.join(map(str, unpack('4B', p)))

def writeFloat(raw):
    # this is just how floats get printed...
    return '{0:.6f}'.format(raw)

xml_formats = {
    1  : { 'names' : ['void']},
    2  : { 'type' : 'b',  'count' : 1,  'names' : ['s8']},
    3  : { 'type' : 'B',  'count' : 1,  'names' : ['u8']},
    4  : { 'type' : 'h',  'count' : 1,  'names' : ['s16']},
    5  : { 'type' : 'H',  'count' : 1,  'names' : ['u16']},
    6  : { 'type' : 'i',  'count' : 1,  'names' : ['s32']},
    7  : { 'type' : 'I',  'count' : 1,  'names' : ['u32']},
    8  : { 'type' : 'q',  'count' : 1,  'names' : ['s64']},
    9  : { 'type' : 'Q',  'count' : 1,  'names' : ['u64']},
    10 : { 'type' : 'B',  'count' : -1, 'names' : ['bin', 'binary'], 'fromStr' : None},
    11 : { 'type' : 'B',  'count' : -1, 'names' : ['str', 'string'], 'fromStr' : None},
    12 : { 'type' : 'I',  'count' : 1,  'names' : ['ip4'], 'fromStr' : parseIP, 'toStr' : writeIP},
    13 : { 'type' : 'I',  'count' : 1,  'names' : ['time']}, # unix timestamp
    14 : { 'type' : 'f',  'count' : 1,  'names' : ['float', 'f'], 'fromStr' : float, 'toStr' : writeFloat},
    15 : { 'type' : 'd',  'count' : 1,  'names' : ['double', 'd'], 'fromStr' : float, 'toStr' : writeFloat},
    16 : { 'type' : 'b',  'count' : 2,  'names' : ['2s8']},
    17 : { 'type' : 'B',  'count' : 2,  'names' : ['2u8']},
    18 : { 'type' : 'h',  'count' : 2,  'names' : ['2s16']},
    19 : { 'type' : 'H',  'count' : 2,  'names' : ['2u16']},
    20 : { 'type' : 'i',  'count' : 2,  'names' : ['2s32']},
    21 : { 'type' : 'I',  'count' : 2,  'names' : ['2u32']},
    22 : { 'type' : 'q',  'count' : 2,  'names' : ['2s64', 'vs64']},
    23 : { 'type' : 'Q',  'count' : 2,  'names' : ['2u64', 'vu64']},
    24 : { 'type' : 'f',  'count' : 2,  'names' : ['2f'], 'fromStr' : float, 'toStr' : writeFloat},
    25 : { 'type' : 'd',  'count' : 2,  'names' : ['2d', 'vd'], 'fromStr' : float, 'toStr' : writeFloat},
    26 : { 'type' : 'b',  'count' : 3,  'names' : ['3s8']},
    27 : { 'type' : 'B',  'count' : 3,  'names' : ['3u8']},
    28 : { 'type' : 'h',  'count' : 3,  'names' : ['3s16']},
    29 : { 'type' : 'H',  'count' : 3,  'names' : ['3u16']},
    30 : { 'type' : 'i',  'count' : 3,  'names' : ['3s32']},
    31 : { 'type' : 'I',  'count' : 3,  'names' : ['3u32']},
    32 : { 'type' : 'q',  'count' : 3,  'names' : ['3s64']},
    33 : { 'type' : 'Q',  'count' : 3,  'names' : ['3u64']},
    34 : { 'type' : 'f',  'count' : 3,  'names' : ['3f'], 'fromStr' : float, 'toStr' : writeFloat},
    35 : { 'type' : 'd',  'count' : 3,  'names' : ['3d'], 'fromStr' : float, 'toStr' : writeFloat},
    36 : { 'type' : 'b',  'count' : 4,  'names' : ['4s8']},
    37 : { 'type' : 'B',  'count' : 4,  'names' : ['4u8']},
    38 : { 'type' : 'h',  'count' : 4,  'names' : ['4s16']},
    39 : { 'type' : 'H',  'count' : 4,  'names' : ['4u16']},
    40 : { 'type' : 'i',  'count' : 4,  'names' : ['4s32', 'vs32']},
    41 : { 'type' : 'I',  'count' : 4,  'names' : ['4u32', 'vu32']},
    42 : { 'type' : 'q',  'count' : 4,  'names' : ['4s64']},
    43 : { 'type' : 'Q',  'count' : 4,  'names' : ['4u64']},
    44 : { 'type' : 'f',  'count' : 4,  'names' : ['4f', 'vf'], 'fromStr' : float, 'toStr' : writeFloat},
    45 : { 'type' : 'd',  'count' : 4,  'names' : ['4d'], 'fromStr' : float, 'toStr' : writeFloat},
    46 : { 'names' : ['attr']},
    #47 : { 'names' : ['array']}, # TODO: how does this work?
    48 : { 'type' : 'b',  'count' : 16, 'names' : ['vs8']},
    49 : { 'type' : 'B',  'count' : 16, 'names' : ['vu8']},
    50 : { 'type' : 'h',  'count' : 8,  'names' : ['vs16']},
    51 : { 'type' : 'H',  'count' : 8,  'names' : ['vu16']},
    52 : { 'type' : 'b',  'count' : 1,  'names' : ['bool', 'b']},
    53 : { 'type' : 'b',  'count' : 2,  'names' : ['2b']},
    54 : { 'type' : 'b',  'count' : 3,  'names' : ['3b']},
    55 : { 'type' : 'b',  'count' : 4,  'names' : ['4b']},
    56 : { 'type' : 'b',  'count' : 16, 'names' : ['vb']}
}

# little less boilerplate for writing
for key, val in xml_formats.items():
    xml_formats[key]['name'] = xml_formats[key]['names'][0]

xml_types = {}
for key, val in xml_formats.items():
    for n in val['names']:
        xml_types[n] = key
xml_types['nodeStart'] = 1
xml_types['nodeEnd'] = 190
xml_types['endSection'] = 191
