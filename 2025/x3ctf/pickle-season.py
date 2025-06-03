targets = [
    674, 716, 764, 655, 699, 648, 763, 676, 663, 763,
    656, 755, 706, 658, 717, 675, 658, 717, 672, 656,
    756, 711, 693, 645, 711, 700, 753, 679, 746
]

targets_bytes = [t % 256 for t in targets]

initial_byte = (-42) % 256  # 214

prev = initial_byte
chars = []
for tb in targets_bytes:
    char = prev ^ tb
    chars.append(char)
    prev = tb

flag = ''.join(chr(c) for c in chars)

print(flag[::-1])