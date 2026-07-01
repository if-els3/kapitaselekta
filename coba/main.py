plain = 0x0123456789ABCDEF
key = 0x9876543210FEDCBA

def hex_nib(data, panjang=16):
    hasil = []
    for i in range(panjang):
        nib = (data >> (4 * i )) & 0xf
        hasil.append(nib)

    hasil.reverse()
    return hasil

def nib_hex(data, panjang=16):
    hasil = 0
    for i in range(panjang):
        val = (data[i] << 4 * (panjang - (i + 1))) & 0xffffffffffffffff
        hasil |= val
    
    return hasil


def add_key(plain, key):
    hasil = []
    for i in range(16):
        hasil.append(plain[i] ^ key[i])
    return hasil


SBOX = [
    0x7, 0x4, 0xa, 0x9,
    0x1, 0xf, 0xb, 0x0,
    0xc, 0x3, 0x2, 0x6,
    0x8, 0xe, 0xd, 0x5
]

def sbox_sub(data, sbox=SBOX):
    hasil = []
    for i in range(16):
        sboxed = sbox[data[i]]
        hasil.append(sboxed)
    return hasil


def into_4_words(data):
    w0 = data[0:4]
    w1 = data[4:8]
    w2 = data[8:12]
    w3 = data[12:16]

    return w0, w1, w2, w3

def gf_mul2(nilai):
    nilai &= 0xf
    hasil = (nilai << 1) & 0xf

    if nilai & 0b1000:
        hasil ^= 0b0011
    
    return hasil

M = [
    9, 8,
    8, 9
]

def gf_mul8(nilai):
    return gf_mul2(gf_mul2(gf_mul2(nilai)))

def gf_mul9(nilai):
    return gf_mul8(nilai) ^ nilai

def kali_matrix(w1, w2):
    k0 = gf_mul9(w1) ^ gf_mul8(w2)
    k1 = gf_mul8(w1) ^ gf_mul9(w2)
    return k0, k1

def fungsi_g(word):
    g0 = word[0]
    g1 = word[1]
    g2 = word[2]
    g3 = word[3]

    g4, g5 = kali_matrix(g1, g2)

    return g0, g1, g2, g3, g4, g5

def fungsi_h(word_6):
    h0 = word_6[0] ^ word_6[4]
    h1 = word_6[1] ^ word_6[5]
    h2 = word_6[2] ^ word_6[5]
    h3 = word_6[3] ^ word_6[4]

    return h0, h1, h2, h3

def fungsi_mix(data):
    words = into_4_words(data)
    hasil = []
    for i in range(4):
        hasil_g = fungsi_g(words[i])
        hasil_h = fungsi_h(hasil_g)
        hasil.extend(hasil_h)
    return hasil



PBOX = [
    4, 5, 6, 7,
    8, 9, 10, 11,
    12, 13, 14, 15,
    0, 1, 2, 3
]

def permutation(data, pbox=PBOX):
    hasil = []
    for i in range(16):
        pboxed = data[pbox[i]]
        hasil.append(pboxed)
    
    return hasil

def visualize(data):
    print(f'0x{data:016X}')


def winx_main(plain, key):
    plain_nib = hex_nib(plain)
    key_nib = hex_nib(key)
    A = add_key(plain_nib, key_nib)
    B = sbox_sub(A)
    C = fungsi_mix(B) # Beda di sini aja tadi
    D = permutation(C)

    chiper = nib_hex(D)
    visualize(chiper)

    return chiper

winx_main(plain, key)

