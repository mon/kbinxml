# kbinxml

An encoder/decoder for Konami's binary XML format, used in some of their games.

### Setup:
`pip install bitarray`

Python 2 only:  
`pip install future`

```python
In [1]: from kbinxml import KBinXML
In [2]: text = KBinXML('<?xml version="1.0"?><root __type="str">Hello, world!</root>')
In [3]: text.to_binary()
Out[4]: '\xa0B\x80\x7f\x00\x00\x00\x08\x0b\x04\xdfM9\xfe\xff\x00\x00\x00\x00\x14\x00\x00\x00\x0eHello, world!\x00\x00\x00'

In [5]: bin = KBinXML(Out[4])
In [6]: bin.to_text()
Out[7]: '<?xml version="1.0" encoding="UTF_8"?>\n<root __type="str">Hello, world!</root>\n'
```