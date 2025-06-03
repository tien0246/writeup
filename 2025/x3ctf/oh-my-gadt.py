from collections import defaultdict

def number_to_bytes(n):
    bytes_list = []
    while n > 0:
        bytes_list.append(n % 256)
        n = n // 256
    bytes_list.reverse()
    return bytes_list

n = 2205967053642207131367982253372196254666549571698892523008302353266425115464942068759663110459718064363978392428938015071
bytes_list = number_to_bytes(n)

reverse_map = defaultdict(list)
for x in range(256):
    y = (6 * (x**6) + 2 * (x**3) + x) % 256
    reverse_map[y].append(x)

def reverse_t4(bytes_list):
    for _ in range(3):
        if not bytes_list:
            continue
        xor_prev = 0
        for b in bytes_list[:-1]:
            xor_prev ^= b
        a = bytes_list[-1] ^ xor_prev
        bytes_list = [a] + bytes_list[:-1]
    return bytes_list

def reverse_t3(transformed):
    if not transformed:
        return []
    original = [transformed[-1]]
    for i in range(len(transformed) - 1):
        original.append(transformed[i] ^ transformed[i+1])
    return original

def reverse_t2(bytes_list):
    original = []
    for y in bytes_list:
        possible_x = reverse_map.get(y, [])
        possible_x_filtered = [x for x in possible_x if 32 <= x <= 126]
        if not possible_x_filtered:
            possible_x_filtered = possible_x
        if not possible_x_filtered:
            possible_x_filtered = [0]
        original.append(possible_x_filtered[0])
    return original

def reverse_t1(bytes_list):
    chunk_size = 4
    chunks = [bytes_list[i:i+chunk_size] for i in range(0, len(bytes_list), chunk_size)]
    original_chunks = []
    for i, chunk in enumerate(chunks):
        if len(chunk) < chunk_size:
            original_chunks.append(chunk)
            continue
        rotate_by = i % chunk_size
        rotated = chunk[-rotate_by:] + chunk[:-rotate_by] if rotate_by != 0 else chunk
        original_chunks.append(rotated)
    original = []
    for chunk in original_chunks:
        original.extend(chunk)
    return original

for _ in range(13):
    bytes_list = reverse_t4(bytes_list)
    bytes_list = reverse_t3(bytes_list)
    bytes_list = reverse_t2(bytes_list)
    bytes_list = reverse_t1(bytes_list)

flag = bytes(bytes_list).decode('ascii', errors='ignore')
print("Flag:", flag)