import random

scrambled_hex = "1e1f7e731f69781e1b646e19196e75191e781975196e757e671219666d6d1f756f6465510b0b0b57"
scrambled = [int(scrambled_hex[i:i+2], 16) for i in range(0, len(scrambled_hex), 2)]
chunk_size = 4
chunks = [scrambled[i:i+chunk_size] for i in range(0, len(scrambled), chunk_size)]

def unshuffle(chunks, seed):
    order = list(range(len(chunks)))
    random.seed(seed)
    random.shuffle(order)
    paired = list(zip(order, chunks))
    paired.sort(key=lambda x: x[0])
    return [b for _, chunk in paired for b in chunk]

for seed in range(15):
    candidate = unshuffle(chunks, seed)
    for key in range(256):
        decoded = "".join(chr(b ^ key) for b in candidate)
        if "ENO{" in decoded:
            print("Seed:", seed, "Key:", key, "->", decoded)
            
            
            
# Seed: 0 Key: 42 -> GG5_1ND3M83L4R3_3D_T3D_3!!!}45TY5CR4ENO{
# Seed: 1 Key: 42 -> M83LENO{!!!}3D_TGG5_4R3_45TY3D_35CR41ND3
# Seed: 2 Key: 42 -> !!!}ENO{M83L1ND33D_345TY4R3_3D_TGG5_5CR4
# Seed: 3 Key: 42 -> 3D_345TYGG5_!!!}3D_T5CR41ND3M83LENO{4R3_
# Seed: 4 Key: 42 -> 1ND3GG5_5CR4!!!}ENO{M83L4R3_3D_345TY3D_T
# Seed: 5 Key: 42 -> 3D_31ND345TY5CR4ENO{GG5_M83L3D_T4R3_!!!}
# Seed: 6 Key: 42 -> 4R3_ENO{3D_T1ND33D_345TYM83LGG5_5CR4!!!}
# Seed: 7 Key: 42 -> 3D_T1ND3ENO{5CR43D_3!!!}GG5_4R3_45TYM83L
# Seed: 8 Key: 42 -> 4R3_M83L5CR4!!!}3D_3ENO{GG5_3D_T45TY1ND3
# Seed: 9 Key: 42 -> 4R3_M83L3D_31ND3GG5_ENO{3D_T!!!}5CR445TY
# Seed: 10 Key: 42 -> ENO{3D_35CR4M83L3D_T45TYGG5_1ND34R3_!!!}
# =>> flag: ENO{5CR4M83L3D_3GG5_4R3_1ND33D_T45TY!!!}