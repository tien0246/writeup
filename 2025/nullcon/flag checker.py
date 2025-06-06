encrypted = [
    0xF8, 0xA8, 0xB8, 0x21, 0x60, 0x73, 0x90, 0x83, 0x80, 0xC3,
    0x9B, 0x80, 0xAB, 0x09, 0x59, 0xD3, 0x21, 0xD3, 0xDB, 0xD8,
    0xFB, 0x49, 0x99, 0xE0, 0x79, 0x3C, 0x4C, 0x49, 0x2C, 0x29,
    0xCC, 0xD4, 0xDC, 0x42
]

flag = []
for i in range(34):
    byte = encrypted[i]
    rotated = ((byte >> 3) | ((byte << 5) & 0xFF)) & 0xFF
    after_sub = (rotated - i) % 256
    original = after_sub ^ 0x5A
    flag.append(chr(original))

print(''.join(flag))