#!/usr/bin/env python3
"""
extract_stream_msb.py

Stream-extract low-4 bits (last 4 bits) of R,G,B from an image along diagonals (x+y=d),
append nibble bits MSB->LSB (bit3,2,1,0), form bytes MSB-first (first extracted bit -> bit7),
write continuous payload to a .bin file, and detect+extract an embedded PNG (if present)
by streaming until IEND is encountered.

Usage:
    python extract_stream_msb.py /path/to/image.png /path/to/output_payload.bin

Outputs:
    - payload file with continuous bytes (MSB-first packing)
    - If a PNG is found in the stream, an extracted PNG file payload_extracted.png is saved.
"""

import sys
from collections import deque
from PIL import Image
import os

PNG_SIG = b'\x89PNG\r\n\x1a\n'

def try_parse_png_complete(png_bytes):
    """
    Given bytes starting at PNG signature, attempt to parse PNG chunks until IEND.
    If we have enough bytes to reach IEND, return the full PNG bytes; otherwise return None.
    """
    if not png_bytes.startswith(PNG_SIG):
        return None
    offset = len(PNG_SIG)
    total_len = len(png_bytes)
    try:
        while True:
            # chunk length (4) + chunk type (4) = 8 header bytes
            if offset + 8 > total_len:
                return None
            length = int.from_bytes(png_bytes[offset:offset+4], 'big')
            ctype = png_bytes[offset+4:offset+8]
            offset += 8
            # ensure we have data + CRC
            if offset + length + 4 > total_len:
                return None
            # skip data + CRC
            offset += length + 4
            if ctype == b'IEND':
                # full PNG available
                return png_bytes[:offset]
    except Exception:
        return None

def stream_extract_rgb_low4_msb_image(img_path, out_payload_path, out_png_path=None):
    """
    Stream the extraction and write payload bytes MSB-first into out_payload_path.
    Watch for PNG signature; if found, collect until IEND and write to out_png_path.
    """
    img = Image.open(img_path).convert("RGBA")
    pixels = img.load()
    width, height = img.size

    # Prepare output
    out_dir = os.path.dirname(out_payload_path) or "."
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    f_out = open(out_payload_path, "wb")

    rolling = deque(maxlen=len(PNG_SIG))  # rolling bytes for signature detection
    found_png = False
    png_buf = bytearray()
    png_start_byte_offset = None

    # Byte assembly (MSB-first): shift left in as bits arrive
    current_byte = 0
    bit_count = 0
    bytes_written = 0

    try:
        # Sweep diagonals x + y = d, left->right
        for d in range(width + height):
            for y in reversed(range(height)):
                x = d - y
                if not (0 <= x < width):
                    continue
                r, g, b, a = pixels[x, y]  # RGBA tuple
                # Channel order fixed to RGB
                for v in (r, g, b):
                    # append last four bits MSB-first: bit3,2,1,0
                    for bitpos in (3, 2, 1, 0):
                        bit = (v >> bitpos) & 1
                        # MSB-first byte assembly: shift left and OR-in
                        current_byte = ((current_byte << 1) | bit) & 0xFF
                        bit_count += 1
                        if bit_count == 8:
                            # we've completed a byte
                            bval = current_byte & 0xFF
                            f_out.write(bytes([bval]))
                            bytes_written += 1
                            # rolling signature check
                            rolling.append(bval)
                            if (not found_png) and bytes(rolling) == PNG_SIG:
                                # PNG signature detected; start collecting from signature
                                found_png = True
                                png_start_byte_offset = bytes_written - len(PNG_SIG)
                                png_buf = bytearray(PNG_SIG)
                                # (we do not stop writing to payload file)
                            elif found_png:
                                # continue collecting bytes for the PNG
                                png_buf.append(bval)
                                complete = try_parse_png_complete(png_buf)
                                if complete is not None:
                                    # full PNG parsed; write it out
                                    if out_png_path is None:
                                        out_png_path = os.path.join(out_dir, "payload_extracted.png")
                                    with open(out_png_path, "wb") as pf:
                                        pf.write(complete)
                                    print(f"[+] Found PNG signature at payload byte offset {png_start_byte_offset}; extracted to: {out_png_path}")
                                    # We keep the payload file complete and return success
                                    f_out.close()
                                    return {
                                        "payload_path": out_payload_path,
                                        "png_extracted": out_png_path,
                                        "png_offset": png_start_byte_offset,
                                        "bytes_written": bytes_written
                                    }
                            # reset current byte state
                            current_byte = 0
                            bit_count = 0
        # done scanning
    finally:
        f_out.close()

    # finished scanning, no complete PNG found
    if found_png:
        print("[i] PNG signature was detected during streaming, but file was incomplete (IEND not reached).")
    else:
        print("[i] No PNG signature detected in stream.")
    return {
        "payload_path": out_payload_path,
        "png_extracted": None,
        "png_offset": png_start_byte_offset,
        "bytes_written": bytes_written
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_stream_msb.py /path/to/input_image.png /path/to/out_payload.bin [optional out_png_path]")
        sys.exit(1)
    img_path = sys.argv[1]
    out_payload = sys.argv[2]
    out_png = sys.argv[3] if len(sys.argv) >= 4 else None

    print(f"Input image: {img_path}")
    print(f"Payload output: {out_payload}")
    if out_png:
        print(f"PNG extract target: {out_png}")
    else:
        print("PNG will be saved to payload_extracted.png if found in same directory as payload.")

    result = stream_extract_rgb_low4_msb_image(img_path, out_payload, out_png)
    print("Done. Summary:")
    print(result)

if __name__ == "__main__":
    main()
