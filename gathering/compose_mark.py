#!/usr/bin/env python3
"""Composite the generated gathering-03 pigment patch using ffmpeg.

Before running, wall.png must be the recovered record-02 PNG and wall-v3.png
must be the original generated edit. Only these two wall files are written.
No other image, private file, environment variable or network is accessed.
"""
import hashlib
import json
from pathlib import Path
import subprocess

SOURCE_HASH = 'e53d77dac9c1762b895aa8bff66ab138eff44e9e5cca68fac531718ffef31857'


def pixels(raw):
    return subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1', '-i', 'pipe:0',
                           '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:1'],
                          input=raw, capture_output=True, check=True).stdout


def main():
    source = Path('artifacts/gathering/wall.png')
    target = Path('artifacts/gathering/wall-v3.png')
    original = source.read_bytes()
    if hashlib.sha256(original).hexdigest() != SOURCE_HASH:
        raise ValueError('recover the unchanged gathering record-02 wall first')
    filters = ("[1:v]crop=270:156:450:150,format=rgba,"
               "geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
               "a='255*min(1,min(min(X,W-1-X),min(Y,H-1-Y))/12)'[patch];"
               "[0:v][patch]overlay=450:150:format=rgb,format=rgb24[out]")
    run = subprocess.run(['ffmpeg', '-v', 'error', '-threads', '1',
                          '-filter_complex_threads', '1', '-i', str(source), '-i', str(target),
                          '-filter_complex', filters, '-map', '[out]', '-frames:v', '1',
                          '-c:v', 'png', '-pix_fmt', 'rgb24', '-f', 'image2pipe', 'pipe:1'],
                         capture_output=True, check=True)
    before, after = pixels(original), pixels(run.stdout)
    if len(before) != len(after) or len(after) != 1254 * 1254 * 3:
        raise ValueError('unexpected decoded dimensions')
    changed = outside = 0
    for y in range(1254):
        for x in range(1254):
            i = (y * 1254 + x) * 3
            if before[i:i+3] != after[i:i+3]:
                changed += 1
                if not (450 <= x < 720 and 150 <= y < 306):
                    outside += 1
    if outside or changed < 1000:
        raise ValueError('painting preservation check failed')
    proof = {'source_sha256': SOURCE_HASH,
             'rectangle': {'x': 450, 'y': 150, 'width': 270, 'height': 156},
             'edge_fade_pixels': 12, 'changed_pixels': changed,
             'changed_pixels_outside_rectangle': outside,
             'preserved_pixels_outside_rectangle': 1254 * 1254 - 270 * 156,
             'wall_sha256': hashlib.sha256(run.stdout).hexdigest(),
             'compositing': 'ffmpeg crop, edge alpha and overlay; no outside pixel changed'}
    target.write_bytes(run.stdout)
    source.write_bytes(run.stdout)
    Path('gathering/checks/round-03/image-preservation.json').write_text(
        json.dumps(proof, indent=2) + '\n')
    print(json.dumps(proof, indent=2))


if __name__ == '__main__':
    main()
