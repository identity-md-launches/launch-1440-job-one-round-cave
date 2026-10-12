#!/usr/bin/env python3
"""Make the required 512px JPEG from an 8-bit RGB/RGBA PNG, using only stdlib.

Baseline JPEG, 4:2:0 sampling, fixed valid Huffman tables, quality approximately 50.
This is a format conversion helper, not a painting generator. Run from repo root.
"""
import math
from pathlib import Path
import struct
import zlib

ZIG = [0,1,8,16,9,2,3,10,17,24,32,25,18,11,4,5,12,19,26,33,40,48,
       41,34,27,20,13,6,7,14,21,28,35,42,49,56,57,50,43,36,29,22,15,
       23,30,37,44,51,58,59,52,45,38,31,39,46,53,60,61,54,47,55,62,63]
QUANT = [16,11,10,16,24,40,51,61,12,12,14,19,26,58,60,55,
         14,13,16,24,40,57,69,56,14,17,22,29,51,87,80,62,
         18,22,37,56,68,109,103,77,24,35,55,64,81,104,113,92,
         49,64,78,87,103,121,120,101,72,92,95,98,112,100,103,99]
COS = [[math.cos((2*x+1)*u*math.pi/16) * (1/math.sqrt(2) if u == 0 else 1)
        for x in range(8)] for u in range(8)]


def png_rgb(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not a PNG')
    pos, compressed, header = 8, bytearray(), None
    while pos < len(data):
        size = int.from_bytes(data[pos:pos+4], 'big')
        tag = data[pos+4:pos+8]
        body = data[pos+8:pos+8+size]
        crc = int.from_bytes(data[pos+8+size:pos+12+size], 'big')
        if zlib.crc32(tag + body) != crc:
            raise ValueError('PNG CRC mismatch')
        if tag == b'IHDR':
            header = struct.unpack('>IIBBBBB', body)
        elif tag == b'IDAT':
            compressed.extend(body)
        elif tag == b'IEND':
            break
        pos += size + 12
    if header is None:
        raise ValueError('missing PNG header')
    width, height, depth, color, compression, filtering, interlace = header
    if depth != 8 or color not in (2,6) or compression or filtering or interlace:
        raise ValueError('requires noninterlaced 8-bit RGB or RGBA PNG')
    channels = 3 if color == 2 else 4
    stride = width * channels
    raw = zlib.decompress(compressed)
    if len(raw) != (stride+1)*height:
        raise ValueError('PNG data size mismatch')
    rows, previous = [], bytearray(stride)
    for y in range(height):
        start = y*(stride+1)
        mode = raw[start]
        row = bytearray(raw[start+1:start+1+stride])
        for i in range(stride):
            a = row[i-channels] if i >= channels else 0
            b = previous[i]
            c = previous[i-channels] if i >= channels else 0
            if mode == 0: p = 0
            elif mode == 1: p = a
            elif mode == 2: p = b
            elif mode == 3: p = (a+b)//2
            elif mode == 4:
                estimate = a+b-c
                da,db,dc = abs(estimate-a),abs(estimate-b),abs(estimate-c)
                p = a if da <= db and da <= dc else (b if db <= dc else c)
            else: raise ValueError('invalid PNG filter')
            row[i] = (row[i]+p)&255
        if channels == 4:
            if any(row[i] != 255 for i in range(3,len(row),4)):
                raise ValueError('transparent PNG requires an explicit background')
            rows.append(bytes(v for i,v in enumerate(row) if i%4 != 3))
        else:
            rows.append(bytes(row))
        previous = row
    return width, height, rows


def resize(width, height, rows, size=512):
    # Area-average each source footprint; no extra image is written.
    result = []
    for y in range(size):
        top, bottom = y*height//size, max(y*height//size+1,(y+1)*height//size)
        row = []
        for x in range(size):
            left, right = x*width//size, max(x*width//size+1,(x+1)*width//size)
            n = (bottom-top)*(right-left)
            rgb = [sum(rows[sy][3*sx+c] for sy in range(top,bottom)
                       for sx in range(left,right))/n for c in range(3)]
            r,g,b = rgb
            row.append((0.299*r+0.587*g+0.114*b-128,
                        -0.168736*r-0.331264*g+0.5*b,
                        0.5*r-0.418688*g-0.081312*b))
        result.append(row)
    return result


def coefficients(block):
    temp = [[sum(block[y][x]*COS[u][x] for x in range(8)) for u in range(8)]
            for y in range(8)]
    natural = [round(sum(temp[y][u]*COS[v][y] for y in range(8))/4/QUANT[v*8+u])
               for v in range(8) for u in range(8)]
    return [natural[i] for i in ZIG]


def jpeg(pixels):
    size = len(pixels)
    if size%16 or any(len(row)!=size for row in pixels):
        raise ValueError('square size must be a multiple of 16')
    output = bytearray(b'\xff\xd8')
    def segment(marker, data):
        output.extend(bytes([255,marker])+struct.pack('>H',len(data)+2)+data)
    segment(0xe0,b'JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00')
    segment(0xdb,bytes([0]+[QUANT[i] for i in ZIG]))
    segment(0xc0,bytes([8])+struct.pack('>HH',size,size)+bytes([3,1,0x22,0,2,0x11,0,3,0x11,0]))
    ac_symbols = [0,0xf0]+[run*16+n for run in range(16) for n in range(1,11)]
    ac_codes = {value:code for code,value in enumerate(ac_symbols)}
    segment(0xc4,bytes([0]+[0,0,0,12]+[0]*12+list(range(12))))
    segment(0xc4,bytes([0x10]+[0]*7+[len(ac_symbols)]+[0]*8+ac_symbols))
    segment(0xda,bytes([3,1,0,2,0,3,0,0,63,0]))
    accumulator, count = 0,0
    def bits(value, n):
        nonlocal accumulator,count
        accumulator=(accumulator<<n)|value
        count+=n
        while count>=8:
            count-=8
            byte=(accumulator>>count)&255
            output.append(byte)
            if byte==255:output.append(0)
        accumulator &= (1<<count)-1
    def magnitude(value):
        n=abs(value).bit_length()
        return n, value if value>=0 else value+(1<<n)-1
    previous=[0,0,0]
    def encode(block,component):
        coeff=coefficients(block)
        delta=coeff[0]-previous[component]
        previous[component]=coeff[0]
        n,value=magnitude(delta)
        if n>11:raise ValueError('DC coefficient too large')
        bits(n,4);bits(value,n)
        zeros=0
        for value in coeff[1:]:
            if not value:
                zeros+=1
                continue
            while zeros>=16:
                bits(ac_codes[0xf0],8);zeros-=16
            n,value=magnitude(value)
            if n>10:raise ValueError('AC coefficient too large')
            bits(ac_codes[zeros*16+n],8);bits(value,n);zeros=0
        if zeros:bits(ac_codes[0],8)
    for y in range(0,size,16):
        for x in range(0,size,16):
            for dy,dx in ((0,0),(0,8),(8,0),(8,8)):
                encode([[pixels[y+dy+j][x+dx+i][0] for i in range(8)] for j in range(8)],0)
            for component in (1,2):
                encode([[sum(pixels[y+j*2+dy][x+i*2+dx][component]
                             for dy in (0,1) for dx in (0,1))/4
                         for i in range(8)] for j in range(8)],component)
    if count:bits((1<<(8-count))-1,8-count)
    output.extend(b'\xff\xd9')
    return bytes(output)


if __name__ == '__main__':
    source = Path('artifacts/gathering/wall.png')
    target = Path('dist/gathering/03.jpg')
    width,height,rows = png_rgb(source.read_bytes())
    encoded = jpeg(resize(width,height,rows))
    if len(encoded)>=100000:
        raise SystemExit('JPEG exceeds file size limit')
    target.write_bytes(encoded)
    print(f'{target}: 512x512 baseline JPEG, {len(encoded)} bytes')
