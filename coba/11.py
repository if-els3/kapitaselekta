pt  = 0x0123456789ABCDEF      # 16 digit penuh
key = 0x9876543210FEDCBA

jumlah_round = 4

SBOX = [0x7, 0x4, 0xA, 0x9, 0x1, 0xF, 0xB, 0x0,
        0xC, 0x3, 0x2, 0x6, 0x8, 0xE, 0xD, 0x5]

permutasi = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0, 1, 2, 3]

M = [[1, 3, 4, 6],
     [3, 1, 6, 4],
     [4, 6, 1, 3],
     [6, 4, 3, 1]]

def xorKey(pt, key):
    return pt ^ key

def sub_sbox(a):
    n = 16
    hasil = 0
    for i in range(n):                              # i = posisi, 0 = paling kiri
        nibble = (a >> ((n - 1 - i) * 4)) & 0xF
        hasil |= SBOX[nibble] << ((n - 1 - i) * 4)
    return hasil

def sub_permutasi(b):
    n = len(permutasi)
    out = 0
    for i in range(n):
        nibble = (b >> ((n - 1 - permutasi[i]) * 4)) & 0xF   # out[i] = in[permutasi[i]]
        out |= nibble << ((n - 1 - i) * 4)
    return out

def kali_gf(a, b):
    hasil = 0
    for _ in range(4):
        if b & 1:
            hasil ^= a
        carry = a & 0x8
        a <<= 1
        if carry:
            a ^= 0x1F            # ganti RED sesuai polinomial field
        a &= 0xF
        b >>= 1
    return hasil

def mix_nibbles(c, jumlah_nibble):
    s = len(M)                                      # ukuran matriks otomatis
    n = jumlah_nibble
    out = 0
    for grup in range(n // s):
        base = grup * s
        v = [(c >> ((n - 1 - (base + j)) * 4)) & 0xF for j in range(s)]
        for i in range(s):
            akum = 0
            for j in range(s):
                akum ^= kali_gf(M[i][j], v[j])
            out |= akum << ((n - 1 - (base + i)) * 4)
    return out

def round(pt, key):
    a = xorKey(pt, key)
    b = sub_sbox(a)
    c = sub_permutasi(b)
    d = mix_nibbles(c, 16)
    return d

hasil = pt
for i in range(jumlah_round):
    hasil = round(hasil, key)
    print(f"hasil round {i+1}: {hasil:016X}")

print(f"ciphertext   : {hasil:016X}")