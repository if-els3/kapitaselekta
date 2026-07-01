SBOX = [
    0x2, 0xD, 0xC, 0xB, 0xF, 0xE, 0x0, 0x9, 0x7, 0xA, 0x6, 0x3, 0x1, 0x8, 0x4, 0x5
]

PERM = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15 ]

def split(data):
    hasil = []
    for i in range (16):
        nibble = (data >> (60-i*4)) & 0xf
        hasil.append(nibble)
    return hasil

def combine(data):
    hasil = 0
    for i in range (16):
        hasil |= (data[i] & 0xf) << (60-i*4)
    return hasil

def permutasi(data):
    hasil = []
    for i in range(16):
        nib = PERM[i]
        hasil.append(data [nib])
    return hasil

def subsbox(data):
    hasil = []
    for i in range (16):
        hasil.append(SBOX[data[i]])
    return hasil

def xorKey(pt,key):
    hasil = []
    for i in range(16):
        hasil.append(pt[i] ^ key[i])
    return hasil

def gf(a, b):
    result = 0
    a = a& 0x0f
    b = b& 0x0f
    for i in range(4):
        if b&1:
            result ^= a
        a <<= 1
        hi_bit = a &0x10
        if hi_bit:
            a ^=0x19
        b >>= 1
    return result

def fungsi_fm(data):
    hasil =[]
    for i in range (4):
        base = i*4
        b0 = data[base]
        b1 = data[base + 1]
        b2 = data[base + 2]
        b3 = data[base + 3]
    
        g0 = b1 ^ b2
        g1 = b0 ^ b3

        h0, h1 = kalimatriks(g0,g1)

        c0 = b0 ^ h0
        c1 = b1 ^ h1
        c2 = b2 ^ h1
        c3 = b3 ^ h0

        hasil.extend([c0, c1, c2, c3])
    return hasil



def kalimatriks(g0, g1):
    h0 = gf(8,g0) ^ gf(9,g1)
    h1 = gf(9,g0) ^ gf(8,g1)

    return h0,h1

def encrypt(pt, key):
    temp1 = split(pt)
    temp2 = split(key)
    temp3 = xorKey(temp1, temp2)
    sbox = subsbox(temp3)
    fm = fungsi_fm(sbox)
    ct = permutasi (fm)
    return combine(ct), combine(temp3), combine(sbox), combine(fm)

if __name__ == "__main__":
    pt = 0x0123456789ABCDEF
    key = 0x0E814729A3B5FC6D
    ct, temp3, sbox, fm = encrypt(pt, key)

    print (f"Plaintext : {pt:016x} ")
    print (f"key : {key:016x} ")
    print (f"xorK : {temp3:016x} ")
    print (f"sbox : {sbox:016x} ")
    print (f"FM : {fm:016x} ")
    print (f"ct : {ct:016x} ")