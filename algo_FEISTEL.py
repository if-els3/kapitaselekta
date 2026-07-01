# =====================================================================
#  ALGORITMA FEISTEL-LIKE CIPHER  -  2 Round (Desain Kustom)
#  Alur: XOR K0/K2 --> F(x) --> XOR output_pasangan --> XOR K1/K3/K4/K5 --> Swap
#  Ukuran Blok : 64-bit (4 x 16-bit)
#  Ukuran Kunci: 96-bit (6 x 16-bit)
# =====================================================================


# #####################################################################
# #  BAGIAN 1 : KODE MURNI
# #####################################################################

SBOX = [0xe, 0x4, 0xb, 0x2, 0x3, 0x8, 0x0, 0x9,
        0x1, 0xa, 0x7, 0xf, 0x6, 0xc, 0x5, 0xd]

M = [
    [1, 2, 4, 6],
    [2, 1, 6, 4],
    [4, 6, 1, 2],
    [6, 4, 2, 1]
]

def gf_mul(a, b):
    result = 0
    for _ in range(4):
        if b & 1:
            result ^= a
        b >>= 1
        a <<= 1
        if a & 0x10:
            a ^= 0x13
    return result & 0xF

def fungsi_sbox(val):
    result = 0
    for i in range(4):
        nibble = (val >> (i * 4)) & 0xF
        result |= SBOX[nibble] << (i * 4)
    return result

def fungsi_matriks(val):
    nibbles = [(val >> (i * 4)) & 0xF for i in range(4)]
    result = 0
    for row_idx, row in enumerate(M):
        cell = 0
        for col in range(4):
            cell ^= gf_mul(row[col], nibbles[col])
        result |= cell << (row_idx * 4)
    return result

def fungsi_F(val):
    return fungsi_sbox(fungsi_matriks(fungsi_sbox(val)))

def fungsi_xor_kunci(inp, key):
    return inp ^ key

def fungsi_swap(A, B, C, D):
    return B, C, D, A

def ekspansi_kunci(kunci_96bit):
    K = [(kunci_96bit >> (16 * (5 - i))) & 0xFFFF for i in range(6)]
    return K[0], K[1], K[2], K[3], K[4], K[5]

def enkripsi(plaintext_64bit, kunci_96bit):
    P0 = (plaintext_64bit >> 48) & 0xFFFF
    P1 = (plaintext_64bit >> 32) & 0xFFFF
    P2 = (plaintext_64bit >> 16) & 0xFFFF
    P3 = (plaintext_64bit >>  0) & 0xFFFF

    K0, K1, K2, K3, K4, K5 = ekspansi_kunci(kunci_96bit)

    A  = fungsi_xor_kunci(P0, K0)
    B  = fungsi_xor_kunci(fungsi_F(A) ^ P1, K1)
    C  = fungsi_xor_kunci(P2, K2)
    D  = fungsi_xor_kunci(fungsi_F(C) ^ P3, K3)

    A, B, C, D = fungsi_swap(A, B, C, D)

    B2 = fungsi_xor_kunci(fungsi_F(A) ^ B, K4)
    D2 = fungsi_xor_kunci(fungsi_F(C) ^ D, K5)

    A2, B2, C2, D2 = fungsi_swap(A, B2, C, D2)

    return (A2 << 48) | (B2 << 32) | (C2 << 16) | D2

# ------------ MAIN ------------
plaintext = 0x0123456789ABCDEF
kunci     = 0x9876543210ABCDEF01234567

ciphertext = enkripsi(plaintext, kunci)

print(f"Plaintext  : {plaintext:016X}")
print(f"Kunci      : {kunci:024X}")
print(f"Ciphertext : {ciphertext:016X}")


print("\n" + "="*60 + "\n")


# #####################################################################
# #  BAGIAN 2 : KODE DENGAN KOMENTAR (PENJELASAN)
# #####################################################################


# ---------------------------------------------------------------------
# LOOKUP TABLE : S-BOX
# ---------------------------------------------------------------------
# Berbasis GF(2^4) dengan polinom irredusibel x^4 + x^2 + 1.
# Setiap nibble (4-bit) input dipetakan ke nibble output yang berbeda.
# Tabel : S[0]=e, S[1]=4, S[2]=b, ..., S[f]=d
# Tujuan: memberikan sifat NONLINIER pada transformasi.
# ---------------------------------------------------------------------
SBOX = [0xe, 0x4, 0xb, 0x2, 0x3, 0x8, 0x0, 0x9,
        0x1, 0xa, 0x7, 0xf, 0x6, 0xc, 0x5, 0xd]


# ---------------------------------------------------------------------
# LOOKUP TABLE : MATRIKS MDS (M)
# ---------------------------------------------------------------------
# Matriks 4x4 atas GF(2^4), polinom irredusibel x^4 + x^2 + 1.
# Elemen matriks: {1,2,4,6} dipilih agar bersifat MDS
# (Maximum Distance Separable) -> difusi optimal.
# Tujuan: setiap perubahan 1 nibble input memengaruhi semua nibble output.
# ---------------------------------------------------------------------
M = [
    [1, 2, 4, 6],
    [2, 1, 6, 4],
    [4, 6, 1, 2],
    [6, 4, 2, 1]
]


# ---------------------------------------------------------------------
# HELPER : PERKALIAN DI GF(2^4)
# ---------------------------------------------------------------------
# Di GF(2^4), perkalian dilakukan dengan "shift-and-XOR":
#   - Geser a ke kiri 1 bit = kalikan dengan x.
#   - Jika bit ke-4 muncul (a & 0x10), kurangi dengan polinom = XOR 0x13.
#     (0x13 = x^4 + x + 1; bit x^4 dihapus, sisanya XOR ke a.)
#   - Ulangi 4 kali (derajat maksimal GF(2^4)).
# Input : a, b  (nibble 0..15)
# Output: hasil a*b mod polinom, 1 nibble
# ---------------------------------------------------------------------
def gf_mul(a, b):
    result = 0
    for _ in range(4):                  # iterasi per bit b (4 bit)
        if b & 1:
            result ^= a                 # jika bit b aktif, akumulasi a
        b >>= 1                         # geser b ke kanan
        a <<= 1                         # kalikan a dengan x
        if a & 0x10:
            a ^= 0x13                   # reduksi modulo polinom irredusibel
    return result & 0xF                 # masker 4-bit


# ---------------------------------------------------------------------
# PROSES 1A : FUNGSI S-BOX  ->  substitusi nibble (confusion)
# ---------------------------------------------------------------------
# Di diagram: kotak "S" dalam Fungsi F (lapis pertama & ketiga).
# Input 16-bit dipecah menjadi 4 nibble, masing-masing disubstitusi
# melalui tabel SBOX. Ini lapisan KONFUSI (confusion layer).
# Contoh: 0x9955 -> nibble (LSB ke MSB): [5,5,9,9]
#         S[5]=8, S[5]=8, S[9]=a, S[9]=a -> 0xAA88
# Input : val (16-bit)
# Output: 16-bit hasil substitusi semua nibble
# ---------------------------------------------------------------------
def fungsi_sbox(val):
    result = 0
    for i in range(4):
        nibble = (val >> (i * 4)) & 0xF         # ambil nibble ke-i (dari LSB)
        result |= SBOX[nibble] << (i * 4)       # substitusi & tempatkan kembali
    return result


# ---------------------------------------------------------------------
# PROSES 1B : FUNGSI MATRIKS  ->  difusi antar nibble (diffusion)
# ---------------------------------------------------------------------
# Di diagram: kotak "M" dalam Fungsi F (lapis tengah/kedua).
# Input 16-bit diperlakukan sebagai vektor kolom 4 nibble.
# Dikalikan dengan matriks M atas GF(2^4) -> setiap nibble output
# bergantung pada semua nibble input (avalanche effect).
# Contoh: 0xAA88 -> nibble [8,8,a,a] -> M*[8,8,a,a]^T = [c,c,e,e] -> 0xEECC
# Input : val (16-bit)
# Output: 16-bit hasil perkalian matriks
# ---------------------------------------------------------------------
def fungsi_matriks(val):
    nibbles = [(val >> (i * 4)) & 0xF for i in range(4)]   # pecah jadi 4 nibble
    result = 0
    for row_idx, row in enumerate(M):
        cell = 0
        for col in range(4):
            cell ^= gf_mul(row[col], nibbles[col])          # dot product di GF(2^4)
        result |= cell << (row_idx * 4)
    return result


# ---------------------------------------------------------------------
# PROSES 1 : FUNGSI F  ->  SBox -> Matriks -> SBox
# ---------------------------------------------------------------------
# Di diagram: setiap kotak besar "F" pada cabang kiri/kanan.
# Fungsi F = SBox lapis-1 -> Matriks M -> SBox lapis-2
# Struktur ini menyerupai "mini-round" SPN (Substitution-Permutation Network)
# yang memberikan:
#   - Konfusi dari dua lapis SBox (nonlinear)
#   - Difusi dari lapis Matriks (linear, spreading perubahan)
# Input : val (16-bit, merupakan blok setelah XOR K0 atau K2)
# Output: 16-bit
# ---------------------------------------------------------------------
def fungsi_F(val):
    return fungsi_sbox(fungsi_matriks(fungsi_sbox(val)))
    #           SBox ke-2     Matriks M     SBox ke-1 (dikerjakan kanan ke kiri)


# ---------------------------------------------------------------------
# PROSES 2 : XOR DENGAN KUNCI  ->  AddRoundKey
# ---------------------------------------------------------------------
# Di diagram: lingkaran XOR yang menerima subkunci K_i.
# Melakukan XOR bitwise 16-bit antara data dengan subkunci.
# Tujuan: mencampurkan rahasia (kunci) ke dalam alur data sehingga
# tanpa kunci, output tidak dapat diprediksi.
# Input : inp (16-bit), key (16-bit subkunci)
# Output: 16-bit
# ---------------------------------------------------------------------
def fungsi_xor_kunci(inp, key):
    return inp ^ key                # XOR 16-bit bitwise


# ---------------------------------------------------------------------
# PROSES 3 : FUNGSI SWAP  ->  rotasi blok (permutasi posisi)
# ---------------------------------------------------------------------
# Di diagram: garis-garis menyilang di akhir setiap round.
# Swap diimplementasikan sebagai ROTASI KIRI 1 posisi dari 4 blok:
#   [A, B, C, D]  -->  [B, C, D, A]
# Efek: blok "output baru" (B, D) naik ke posisi input F di round berikutnya,
# sedangkan blok "input lama" (A, C) turun menjadi XOR-partner berikutnya.
# Ini adalah inti mekanisme Feistel: hasil satu sisi menjadi input sisi lain.
# Input : A, B, C, D (masing-masing 16-bit)
# Output: (B, C, D, A)  -- tuple untuk unpacking
# ---------------------------------------------------------------------
def fungsi_swap(A, B, C, D):
    return B, C, D, A               # rotasi kiri: B naik ke posisi pertama


# ---------------------------------------------------------------------
# EKSPANSI KUNCI  ->  memecah kunci 96-bit menjadi 6 subkunci 16-bit
# ---------------------------------------------------------------------
# Kunci 96-bit dipecah secara langsung (tanpa key schedule tambahan):
#   K0 = bit 95..80  (paling signifikan)
#   K1 = bit 79..64
#   K2 = bit 63..48
#   K3 = bit 47..32
#   K4 = bit 31..16
#   K5 = bit 15..0   (paling tidak signifikan)
# Penggunaan:
#   K0, K2 : pre-whitening sebelum F di round 1 (cabang kiri dan kanan)
#   K1, K3 : post-F XOR di round 1
#   K4, K5 : post-F XOR di round 2
# ---------------------------------------------------------------------
def ekspansi_kunci(kunci_96bit):
    K = [(kunci_96bit >> (16 * (5 - i))) & 0xFFFF for i in range(6)]
    return K[0], K[1], K[2], K[3], K[4], K[5]


# ---------------------------------------------------------------------
# ENKRIPSI UTAMA  ->  2-round Feistel-like
# ---------------------------------------------------------------------
# STRUKTUR STATE: plaintext 64-bit dibagi menjadi [P0, P1, P2, P3] @ 16-bit
#   P0 = bit 63..48  |  P1 = bit 47..32  (blok KIRI, pasangan Feistel)
#   P2 = bit 31..16  |  P3 = bit 15..0   (blok KANAN, pasangan Feistel)
#
# Dalam setiap "pasangan Feistel" [P_even, P_odd]:
#   - P_even menjadi INPUT ke fungsi F
#   - P_odd menjadi XOR-PARTNER dari output F
#
# ROUND 1 (dengan pre-whitening K0, K2):
#   A = P0 XOR K0
#   B = F(A) XOR P1 XOR K1       <- output sisi kiri
#   C = P2 XOR K2
#   D = F(C) XOR P3 XOR K3       <- output sisi kanan
#   State baru: [A, B, C, D]
#   Swap: [A,B,C,D] -> [B,C,D,A]
#
# ROUND 2 (tanpa pre-whitening):
#   Setelah swap: A=B_lama, B=C_lama, C=D_lama, D=A_lama
#   B2 = F(A) XOR B XOR K4       <- output sisi kiri round 2
#   D2 = F(C) XOR D XOR K5       <- output sisi kanan round 2
#   State baru: [A, B2, C, D2]
#   Swap: [A,B2,C,D2] -> [B2,C,D2,A]
#
# Ciphertext = [B2, C, D2, A] digabung menjadi 64-bit
# ---------------------------------------------------------------------
def enkripsi(plaintext_64bit, kunci_96bit):
    # --- Pecah plaintext 64-bit menjadi 4 blok 16-bit ---
    P0 = (plaintext_64bit >> 48) & 0xFFFF  # blok 0: MSB
    P1 = (plaintext_64bit >> 32) & 0xFFFF  # blok 1
    P2 = (plaintext_64bit >> 16) & 0xFFFF  # blok 2
    P3 = (plaintext_64bit >>  0) & 0xFFFF  # blok 3: LSB

    # --- Ekspansi kunci ---
    K0, K1, K2, K3, K4, K5 = ekspansi_kunci(kunci_96bit)

    # === ROUND 1 ===
    # Cabang KIRI: pre-whiten P0, lalu F, lalu XOR P1 dan K1
    A = fungsi_xor_kunci(P0, K0)               # A = P0 XOR K0 (pre-whitening)
    B = fungsi_xor_kunci(fungsi_F(A) ^ P1, K1) # B = F(A) XOR P1 XOR K1

    # Cabang KANAN: pre-whiten P2, lalu F, lalu XOR P3 dan K3
    C = fungsi_xor_kunci(P2, K2)               # C = P2 XOR K2 (pre-whitening)
    D = fungsi_xor_kunci(fungsi_F(C) ^ P3, K3) # D = F(C) XOR P3 XOR K3

    # Swap round 1: [A,B,C,D] -> [B,C,D,A]
    A, B, C, D = fungsi_swap(A, B, C, D)
    # Setelah swap: A=B_lama, B=C_lama, C=D_lama, D=A_lama

    # === ROUND 2 ===
    # Cabang KIRI: F dari A (= B lama), XOR B (= C lama), XOR K4
    B2 = fungsi_xor_kunci(fungsi_F(A) ^ B, K4)  # B2 = F(A) XOR B XOR K4

    # Cabang KANAN: F dari C (= D lama), XOR D (= A lama), XOR K5
    D2 = fungsi_xor_kunci(fungsi_F(C) ^ D, K5)  # D2 = F(C) XOR D XOR K5

    # Swap round 2: [A, B2, C, D2] -> [B2, C, D2, A]
    A2, B2, C2, D2 = fungsi_swap(A, B2, C, D2)

    # --- Gabung 4 blok 16-bit menjadi ciphertext 64-bit ---
    return (A2 << 48) | (B2 << 32) | (C2 << 16) | D2


# ------------ MAIN (test vector resmi dari desain) ------------
plaintext = 0x0123456789ABCDEF         # plaintext 64-bit
kunci     = 0x9876543210ABCDEF01234567 # kunci 96-bit

K0, K1, K2, K3, K4, K5 = ekspansi_kunci(kunci)

print(f"Plaintext  : {plaintext:016X}")
print(f"Kunci      : {kunci:024X}")
print(f"K0={K0:04X}  K1={K1:04X}  K2={K2:04X}  K3={K3:04X}  K4={K4:04X}  K5={K5:04X}")

P0 = (plaintext >> 48) & 0xFFFF
P1 = (plaintext >> 32) & 0xFFFF
P2 = (plaintext >> 16) & 0xFFFF
P3 = (plaintext >>  0) & 0xFFFF

# ========================== ROUND 1 ==========================
print(f"\n===============XOR K0===============")
A = P0 ^ K0
print(f"XOR K0      : {A:04X}")            # 9955

print(f"\n===========Fungsi F KIRI============")
s1 = fungsi_sbox(A)
print(f"Sbox        : {s1:04X}")            # AA88
m1 = fungsi_matriks(s1)
print(f"Hasil M     : {m1:04X}")            # EECC
s2 = fungsi_sbox(m1)
print(f"Sbox        : {s2:04X}")            # 5566

print(f"\n===============XOR K1===============")
B = (s2 ^ P1) ^ K1
print(f"XOR F       : {s2 ^ P1:04X}")      # 1001  (F_kiri XOR P1)
print(f"XOR K1      : {B:04X}")             # 4433

print(f"\n===============XOR K2===============")
C = P2 ^ K2
print(f"XOR K2      : {C:04X}")             # 9900

print(f"\n===========Fungsi F KANAN===========")
s1r = fungsi_sbox(C)
print(f"Sbox        : {s1r:04X}")           # AAEE
m1r = fungsi_matriks(s1r)
print(f"Hasil M     : {m1r:04X}")           # 2266
s2r = fungsi_sbox(m1r)
print(f"Sbox        : {s2r:04X}")           # BB00

print(f"\n===============XOR K3===============")
D = (s2r ^ P3) ^ K3
print(f"XOR F       : {s2r ^ P3:04X}")     # 76EF  (F_kanan XOR P3)
print(f"XOR K3      : {D:04X}")             # BB00

A, B, C, D = fungsi_swap(A, B, C, D)
print(f"\nSwap        : {A:04X}{B:04X}{C:04X}{D:04X}")  # 44339900BB009955

# ========================== ROUND 2 ==========================
print(f"\n===========Fungsi F KIRI============")
s1_r2 = fungsi_sbox(A)
print(f"Sbox        : {s1_r2:04X}")         # 3322
m1_r2 = fungsi_matriks(s1_r2)
print(f"Hasil M     : {m1_r2:04X}")         # 1100
s2_r2 = fungsi_sbox(m1_r2)
print(f"Sbox        : {s2_r2:04X}")         # 44EE

print(f"\n===============XOR K4===============")
B2 = (s2_r2 ^ B) ^ K4
print(f"XOR F       : {s2_r2 ^ B:04X}")    # DDEE  (F_kiri XOR B)
print(f"XOR K4      : {B2:04X}")            # DCCD

print(f"\n===========Fungsi F KANAN===========")
s1r_r2 = fungsi_sbox(C)
print(f"Sbox        : {s1r_r2:04X}")        # FFEE
m1r_r2 = fungsi_matriks(s1r_r2)
print(f"Hasil M     : {m1r_r2:04X}")        # DDCC
s2r_r2 = fungsi_sbox(m1r_r2)
print(f"Sbox        : {s2r_r2:04X}")        # CC66

print(f"\n===============XOR K5===============")
D2 = (s2r_r2 ^ D) ^ K5
print(f"XOR F       : {s2r_r2 ^ D:04X}")   # 5533  (F_kanan XOR D)
print(f"XOR K5      : {D2:04X}")            # 1054

A2, B2, C2, D2 = fungsi_swap(A, B2, C, D2)
print(f"\nSwap        : {A2:04X}{B2:04X}{C2:04X}{D2:04X}")  # DCCDBB0010544433
ciphertext = (A2 << 48) | (B2 << 32) | (C2 << 16) | D2
print(f"Cipher      : {ciphertext:016X}")                   # DCCDBB0010544433
