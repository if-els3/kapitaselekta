import unittest

SBOX = [
    0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8,
    0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7,
]

M = [
    [3,2],
    [2,3],
]

RCON = [0x1, 0x2]

def xorKey(s, key):
    return s ^ key

def split(val):
    return [
        (val >> (12-4* i)) & 0xf for i in range (4)
    ]

def combine(nibbles):
    result = 0
    for n in nibbles:
        result = (result << 4) | (n& 0xf)
    return result

def gfmul4(a: int, b:int) -> int:
    p = 0
    for _ in range(4):
        if b&1:
            p ^= a
        hi_bit_set = a& 0x08
        a = (a <<1) & 0x0f
        if hi_bit_set:
            a ^= 0x03
        b >>= 1
    return p

def gf_mult_n(a: int, n: int) -> int:
    """Kalikan nibble dengan konstanta 1, 2, atau 3 di GF(4)."""
    if n == 1:
        return a & 0xF
    if n == 2:
        return gfmul4(a, 2)
    if n == 3:
        return gfmul4(a, 2) ^ (a & 0xF)
    raise ValueError("Konstanta GF(4) harus 1, 2, atau 3")

def sub_nibble(val):
    nibbles = split(val)
    return combine(SBOX[n] for n in nibbles)

def shift_row(val):
    p0, p1, p2, p3 = split(val)
    return combine([p0, p3, p2, p1])

def mix_column(val):
    p0, p1, p2, p3 = split(val)

    def mix_pair(top: int, bottom: int) -> tuple[int, int]:
        out_top = gf_mult_n(top, M[0][0]) ^ gf_mult_n(bottom, M[0][1])
        out_bottom = gf_mult_n(top, M[1][0]) ^ gf_mult_n(bottom, M[1][1])
        return out_top & 0xF, out_bottom & 0xF

    d0, d1 = mix_pair(p0, p1)
    d2, d3 = mix_pair(p2, p3)
    return combine([d0, d1, d2, d3])

def key_add(val, round_key):
    return xorKey (val, round_key) & 0xffff

def key_schedule(key: int) -> tuple[int, int, int]:
    """Bangkitkan K0, K1, K2 dari kunci 16-bit."""
    w = split(key)

    for rnd in range(1, 3):
        w0, w1, w2, w3 = w[-4], w[-3], w[-2], w[-1]
        w4 = w0 ^ SBOX[w3] ^ RCON[rnd - 1]
        w5 = w1 ^ w4
        w6 = w2 ^ w5
        w7 = w3 ^ w6
        w.extend([w4, w5, w6, w7])

    k0 = combine(w[0:4])
    k1 = combine(w[4:8])
    k2 = combine(w[8:12])
    return k0, k1, k2

def format_block(value: int) -> str:
    """Tampilkan 16-bit sebagai 4 nibble biner."""
    nibbles = split(value)
    return " ".join(f"{n:04b}" for n in nibbles)


def encrypt(plaintext: int, key: int) -> int:
    """Enkripsi Mini-AES."""
    k0, k1, k2 = key_schedule(key)
    state = key_add(plaintext, k0)
    state = sub_nibble(state)
    state = shift_row(state)
    state = mix_column(state)
    state = key_add(state, k1)
    state = sub_nibble(state)
    state = shift_row(state)
    state = key_add(state, k2)
    return state & 0xFFFF

plaintext = 0x9C63
key = 0xC3F0

k0, k1, k2 = key_schedule(key)
print("=== Mini-AES (contoh PDF) ===")
print(f"Plaintext : {format_block(plaintext)}  (0x{plaintext:04X})")
print(f"Kunci     : {format_block(key)}  (0x{key:04X})")
print(f"K0        : {format_block(k0)}  (0x{k0:04X})")
print(f"K1        : {format_block(k1)}  (0x{k1:04X})")
print(f"K2        : {format_block(k2)}  (0x{k2:04X})")

ciphertext = encrypt(plaintext, key)
print(f"Ciphertext: {format_block(ciphertext)}  (0x{ciphertext:04X})")

print("\n=== Latihan: kunci AA ===")
latihan_key = 0xAA00
lk0, lk1, lk2 = key_schedule(latihan_key)
print(f"K0: 0x{lk0:04X}, K1: 0x{lk1:04X}, K2: 0x{lk2:04X}")
for pt in (0x0000, 0x8800):
    ct = encrypt(pt, latihan_key)
    print(f"P={format_block(pt)} -> C={format_block(ct)}  (0x{ct:04X})")