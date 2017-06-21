xml_formats = {
    1  : { 'type' : None, 'count' : None, 'pyType' : None,  'names' : ['void']},
    2  : { 'type' : 'b',  'count' : 1,    'pyType' : int,   'names' : ['s8']},
    3  : { 'type' : 'B',  'count' : 1,    'pyType' : int,   'names' : ['u8']},
    4  : { 'type' : 'h',  'count' : 1,    'pyType' : int,   'names' : ['s16']},
    5  : { 'type' : 'H',  'count' : 1,    'pyType' : int,   'names' : ['u16']},
    6  : { 'type' : 'i',  'count' : 1,    'pyType' : int,   'names' : ['s32']},
    7  : { 'type' : 'I',  'count' : 1,    'pyType' : int,   'names' : ['u32']},
    8  : { 'type' : 'q',  'count' : 1,    'pyType' : int,   'names' : ['s64']},
    9  : { 'type' : 'Q',  'count' : 1,    'pyType' : int,   'names' : ['u64']},
    10 : { 'type' : 'c',  'count' : -1,   'pyType' : None, 'names' : ['bin', 'binary'], 'delimiter' : ''},
    11 : { 'type' : 's',  'count' : -1,   'pyType' : None, 'names' : ['str', 'string'], 'delimiter' : ''},
    12 : { 'type' : 'B',  'count' : 4,    'pyType' : int,   'names' : ['ip4'], 'delimiter' : '.'},
    13 : { 'type' : 'I',  'count' : 1,    'pyType' : int,   'names' : ['time']}, # todo: how to print
    14 : { 'type' : 'f',  'count' : 1,    'pyType' : float, 'names' : ['float', 'f']},
    15 : { 'type' : 'd',  'count' : 1,    'pyType' : float, 'names' : ['double', 'd']},
    16 : { 'type' : 'b',  'count' : 2,    'pyType' : int,   'names' : ['2s8']},
    17 : { 'type' : 'B',  'count' : 2,    'pyType' : int,   'names' : ['2u8']},
    18 : { 'type' : 'h',  'count' : 2,    'pyType' : int,   'names' : ['2s16']},
    19 : { 'type' : 'H',  'count' : 2,    'pyType' : int,   'names' : ['2u16']},
    20 : { 'type' : 'i',  'count' : 2,    'pyType' : int,   'names' : ['2s32']},
    21 : { 'type' : 'I',  'count' : 2,    'pyType' : int,   'names' : ['2u32']},
    22 : { 'type' : 'q',  'count' : 2,    'pyType' : int,   'names' : ['2s64', 'vs64']},
    23 : { 'type' : 'Q',  'count' : 2,    'pyType' : int,   'names' : ['2u64', 'vu64']},
    24 : { 'type' : 'f',  'count' : 2,    'pyType' : float, 'names' : ['2f']},
    25 : { 'type' : 'd',  'count' : 2,    'pyType' : float, 'names' : ['2d', 'vd']},
    26 : { 'type' : 'b',  'count' : 3,    'pyType' : int,   'names' : ['3s8']},
    27 : { 'type' : 'B',  'count' : 3,    'pyType' : int,   'names' : ['3u8']},
    28 : { 'type' : 'h',  'count' : 3,    'pyType' : int,   'names' : ['3s16']},
    29 : { 'type' : 'H',  'count' : 3,    'pyType' : int,   'names' : ['3u16']},
    30 : { 'type' : 'i',  'count' : 3,    'pyType' : int,   'names' : ['3s32']},
    31 : { 'type' : 'I',  'count' : 3,    'pyType' : int,   'names' : ['3u32']},
    32 : { 'type' : 'q',  'count' : 3,    'pyType' : int,   'names' : ['3s64']},
    33 : { 'type' : 'Q',  'count' : 3,    'pyType' : int,   'names' : ['3u64']},
    34 : { 'type' : 'f',  'count' : 3,    'pyType' : float, 'names' : ['3f']},
    35 : { 'type' : 'd',  'count' : 3,    'pyType' : float, 'names' : ['3d']},
    36 : { 'type' : 'b',  'count' : 4,    'pyType' : int,   'names' : ['4s8']},
    37 : { 'type' : 'B',  'count' : 4,    'pyType' : int,   'names' : ['4u8']},
    38 : { 'type' : 'h',  'count' : 4,    'pyType' : int,   'names' : ['4s16']},
    39 : { 'type' : 'H',  'count' : 4,    'pyType' : int,   'names' : ['4u16']},
    40 : { 'type' : 'i',  'count' : 4,    'pyType' : int,   'names' : ['4s32', 'vs32']},
    41 : { 'type' : 'I',  'count' : 4,    'pyType' : int,   'names' : ['4u32', 'vu32']},
    42 : { 'type' : 'q',  'count' : 4,    'pyType' : int,   'names' : ['4s64']},
    43 : { 'type' : 'Q',  'count' : 4,    'pyType' : int,   'names' : ['4u64']},
    44 : { 'type' : 'f',  'count' : 4,    'pyType' : float, 'names' : ['4f', 'vf']},
    45 : { 'type' : 'd',  'count' : 4,    'pyType' : float, 'names' : ['4d']},
    46 : { 'type' : None, 'count' : None, 'pyType' : None,  'names' : ['attr']},
    #47 : { 'type' : None, 'count' : None, 'pyType' : None,  'names' : ['array']},
    48 : { 'type' : 'b',  'count' : 16,   'pyType' : int,   'names' : ['vs8']},
    49 : { 'type' : 'B',  'count' : 16,   'pyType' : int,   'names' : ['vu8']},
    50 : { 'type' : 'h',  'count' : 8,    'pyType' : int,   'names' : ['vs16']},
    51 : { 'type' : 'H',  'count' : 8,    'pyType' : int,   'names' : ['vu16']},
    52 : { 'type' : 'b',  'count' : 1,    'pyType' : int,   'names' : ['bool', 'b']},
    53 : { 'type' : 'b',  'count' : 2,    'pyType' : int,   'names' : ['2b']},
    54 : { 'type' : 'b',  'count' : 3,    'pyType' : int,   'names' : ['3b']},
    55 : { 'type' : 'b',  'count' : 4,    'pyType' : int,   'names' : ['4b']},
    56 : { 'type' : 'b',  'count' : 16,   'pyType' : int,   'names' : ['vb']}
}

# little less boilerplate for writing
for key, val in xml_formats.iteritems():
    xml_formats[key]['name'] = xml_formats[key]['names'][0]

xml_types = {}
for key, val in xml_formats.iteritems():
    for n in val['names']:
        xml_types[n] = key
xml_types['nodeStart'] = 1
xml_types['nodeEnd'] = 190
xml_types['endSection'] = 191
