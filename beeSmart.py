import unittest

SBOX1 = [0xC, 0x5, 0x6, 0xB, 0x9, 0x0, 0xA, 0xD, 0x3, 0xE, 0xF, 0x8, 0x4, 0x7, 0x1, 0x2]
SBOX2 = [0x4, 0xA, 0x9, 0x2, 0xD, 0x8, 0x0, 0xE, 0x6, 0xB, 0x1, 0xC, 0x7, 0xF, 0x5, 0x3]

def rotl(var, r_bits, width=32):
    return ((var << r_bits) | (var >> (width - r_bits))) & ((1 << width) - 1)

def split_nibbles_32(x):
    return [
        (x >> (28 - 4 * i)) & 0xF for i in range(8)
    ]

def combine_nibbles_32(nibbles):
    result = 0
    for n in nibbles:
        result = (result << 4) | (n & 0xF)
    return result

def sbox_sub(value, sbox):
    nibbles = split_nibbles_32(value)
    substituted = [
        sbox[n]
        for n in nibbles
    ]
    return combine_nibbles_32(substituted)

def xorkey(val, key):
    """Operasi XOR untuk Key"""
    return val ^ key

def fungsiF(li, ri):
    temp1 = rotl(li, 5, 32)
    temp2 = rotl(li, 1, 32)
    and_result = (temp1 & temp2) ^ ri
    output = and_result ^ temp2

    return output & 0xFFFFFFFF

# ==========================================
# 2. INTEGRASI FUNGSI (ENKRIPSI)
# ==========================================

def beesmart_encrypt(plaintext, key, rounds=1):
    Li = (plaintext >> 32) & 0xFFFFFFFF
    Ri = plaintext & 0xFFFFFFFF
    K1 = (key >> 32) & 0xFFFFFFFF
    K2 = key & 0xFFFFFFFF

    for r in range(rounds):
        Li_sub = sbox_sub(Li, SBOX1)
        Ri_sub = sbox_sub(Ri, SBOX2)
        F = fungsiF(Li_sub, Ri_sub)
        new_L = Ri_sub ^ K1
        new_R = (F ^K2) & 0xFFFFFFFF
        Li, Ri = new_L, new_R

    ciphertext = (((Li & 0xFFFFFFFF) << 32) | (Ri & 0xFFFFFFFF))
    return ciphertext

class TestBeeSmartUnit(unittest.TestCase):
    def test_rotl(self):
        self.assertEqual(rotl(0x12345678,1,32), 0x2468ACF0)
    def test_sbox1(self):
        self.assertEqual(SBOX1[0x0], 0xC)
        self.assertEqual(SBOX1[0xF], 0x2)
    def test_sbox2(self):
        self.assertEqual(SBOX2[0x0], 0x4)
        self.assertEqual(SBOX2[0xF], 0x3)
    def test_fungsiF(self):
        li = 0xAF51D40D
        ri = 0x07B386A6
        self.assertEqual(fungsiF(li, ri), 0x1332AEAC)

class TestBeeSmartIntegration(unittest.TestCase):
    def test_enkripsi_round_2(self):
        plaintext = 0x0123456789ABCDEF
        key = 0x0102030405060708
        ciphertext = beesmart_encrypt(plaintext, key, 2)
        self.assertEqual(ciphertext, 0x06B185A21634A9A4)

if __name__ == '__main__':
    plaintext = 0x0123456789abcdef
    key = 0x0102030405060708
    rounds = 2
