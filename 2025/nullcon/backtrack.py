def decompress(data):
    if len(data) < 4:
        raise ValueError("Invalid data")
    if data[0] == 1:
        return data[4:]
    out = bytearray()
    i = 4
    n = len(data)
    while i < n:
        if i + 1 >= n:
            break
        flag = data[i] | (data[i + 1] << 8)
        i += 2
        bits = 16
        while bits > 0 and i < n:
            if flag & 1:
                if i + 1 >= n:
                    raise ValueError("Incomplete back-reference")
                first = data[i]
                length = (first & 0x0F) + 1
                offset = ((first >> 4) << 8) | data[i + 1]
                i += 2
                if offset > len(out):
                    raise ValueError("Invalid offset")
                src_index = len(out) - offset
                for _ in range(length):
                    out.append(out[src_index])
                    src_index += 1
            else:
                out.append(data[i])
                i += 1
            flag >>= 1
            bits -= 1
    return bytes(out)

with open('data.bin', "rb") as f:
    data = f.read()
decompressed = decompress(data)
with open('output', "wb") as f:
    f.write(decompressed)