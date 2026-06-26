import unittest

SBOX = [0x7, 0x4, 0xA, 0x9, 0x1, 0xF, 0xB, 0x0, 0xC, 0x3, 0x2, 0x6, 0x8, 0xE, 0xD, 0x5]

PERMUTATION = [12, 13, 14, 15, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

# Matriks perkalian GF(2^8)
MATRIX = [
        [1, 3, 4, 6],
        [3, 1, 6, 4],
        [4, 6, 1, 3],
        [6, 4, 3, 1]
        ]

def xorKey(s, key):
	return s ^ key

def SBOX_substitution(data):
    result = 0
    for i in range(16):
        shift = i * 4
        nibble = (data >> shift) & 0xF
        substituted = SBOX[nibble]
        result |= (substituted << shift)
    return result

def permutasi(data):
    nibbles = [(data >> (60 - i * 4)) & 0xF for i in range(16)]

    permuted_data = 0
    for idx in PERMUTATION:
        permuted_data = (permuted_data << 4) | nibbles[idx]
        
    return permuted_data

def gf_mult_4bit(a: int, b: int) -> int:
        """
        Perkalian Galois Field GF(2^4) 
        menggunakan polinomial x^4 + x^3 + x^2 + x + 1.
        Jika terjadi overflow ke bit-4 (melebihi kapasitas 4-bit), 
        kita potong nilainya menggunakan XOR dengan 0xF (biner 1111).
        """
        p = 0
        for _ in range(4):
            if b & 1:
                p ^= a
                
            # Cek apakah bit ke-3 (bernilai 8) sedang aktif sebelum digeser
            hi_bit_set = a & 0x08  
            
            # Geser ke kiri (sama dengan dikali 2) dan batasi di 4-bit
            a = (a << 1) & 0x0F    
            
            if hi_bit_set:
                # Jika bit ke-3 tadinya aktif, geseran di atas menyebabkan
                # angka tumpah ke bit-4. Pangkas dengan polinomial 0xF.
                a ^= 0x0F
                
            b >>= 1
        return p

def kali_matriks(data: int) -> int:
        """
        Fungsi utama yang memecah input 16-bit menjadi 4 bagian (nibble),
        mengalikannya dengan matriks GF, dan menyatukannya kembali.
        """
        # Langkah 1: Ekstraksi 4 nibble (masing-masing 4-bit) dari input 16-bit
        a = [
            (data >> 12) & 0xF, # a0
            (data >> 8) & 0xF,  # a1
            (data >> 4) & 0xF,  # a2
            data & 0xF          # a3
        ]
        
        # Langkah 2: Proses perkalian matriks dan penjumlahan (XOR)
        b = [0] * 4
        for i in range(4):
            b[i] = (
                gf_mult_4bit(MATRIX[i][0], a[0]) ^
                gf_mult_4bit(MATRIX[i][1], a[1]) ^
                gf_mult_4bit(MATRIX[i][2], a[2]) ^
                gf_mult_4bit(MATRIX[i][3], a[3])
            )
        
        # Langkah 3: Gabungkan kembali 4 nibble hasil menjadi 16-bit utuh
        result = (b[0] << 12) | (b[1] << 8) | (b[2] << 4) | b[3]
        return result


def enkripsi(plaintext, key, round):


    for i in range(round):
        xor_key = xorKey(plaintext, key)
        substituted = SBOX_substitution(xor_key)
        permuted_data = permutasi(substituted)
        print(f"[ENK] Round {i+1}: XOR Key = {xor_key:016x}, Substituted = {substituted:016x}, Permuted = {permuted_data:016x}")
    
    return permuted_data   

#fungsi unit testing
class TestLebahUnit(unittest.TestCase):
    def test_xorKeys(self):
        plaintext = 0x1234567890abcdef
        key = 0x9876543210FEDCBA
        expected = 0x9955115599551155
        self.assertEqual(xorKey(plaintext, key), expected)

    def test_SBOX_substitution(self):
        plaintext = 0x9955115599551155
        expected = 0x33FF44FF33FF44FF
        self.assertEqual(SBOX_substitution(plaintext), expected)

    def test_permutasi(self):
        plaintext = 0x33FF44FF33FF44FF
        expected = 0x44FF33FF44FF33FF
        self.assertEqual(permutasi(plaintext), expected)

if __name__ == "__main__":
    plaintext = 0x0123456789abcdef  
    key = 0x9876543210FEDCBA 
    round = 2

    print("=== DATA AWAL ===")
    print("Plaintext  : {:016x}".format(plaintext))
    print("Key        : {:016x}\n".format(key))
    
    xor_key = xorKey(plaintext, key)
    print(f"XOR Key   : {xor_key:016x}")
    substituted = SBOX_substitution(xor_key)
    print(f"SBOX Subst: {substituted:016x}")
    permuted_data = permutasi(substituted)
    print(f"Permutasi : {permuted_data:016x}\n")

    #membagi permutated_data menjadi 4 blok 16-bit  
    block1 = (permuted_data >> 48) & 0xFFFF
    block2 = (permuted_data >> 32) & 0xFFFF
    block3 = (permuted_data >> 16) & 0xFFFF
    block4 = permuted_data & 0xFFFF

    print(f"Blok 1: {block1:04x}, Blok 2: {block2:04x}, Blok 3: {block3:04x}, Blok 4: {block4:04x}")

    kali_matriks_result1 = kali_matriks(block1)
    print(f"Hasil Kali Matriks Blok 1: {kali_matriks_result1:08x}")
    kali_matriks_result2 = kali_matriks(block2)
    print(f"Hasil Kali Matriks Blok 2: {kali_matriks_result2:08x}")
    kali_matriks_result3 = kali_matriks(block3)
    print(f"Hasil Kali Matriks Blok 3: {kali_matriks_result3:08x}")
    kali_matriks_result4 = kali_matriks(block4)
    print(f"Hasil Kali Matriks Blok 4: {kali_matriks_result4:08x}\n")

   


    # Run unit tests    
    # unittest.main()