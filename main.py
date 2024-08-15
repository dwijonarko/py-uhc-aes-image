# -*- coding: utf-8 -*-
"""Hill-AESCBC Cipher_Gambar-UPDATE.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18NExwuHcpAmmp_WD7K3L3QQuSZnX3k5T

Impor Paket
"""

#!pip install pycryptodome

import os
import numpy as np
import time
import matplotlib.pyplot as plt
from scipy.stats import entropy
from functools import reduce
from PIL import Image
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from scipy.stats import entropy

# from google.colab import runtime

"""Fungsi Menyimpan dan Membaca File (digunakan untuk menyimpan dan membaca kunci acak)

"""


def save_key_to_file(key, filename):
    with open(filename, "wb") as f:
        f.write(key)


def load_key_from_file(filename):
    with open(filename, "rb") as f:
        key = f.read()
    return key


"""Fungsi yang dibutuhkan dalam proses UHC"""


# factorisasi bilangan
def factors(n):
    fkt = set(
        reduce(
            list.__add__, ([i, n // i] for i in range(2, int(n**0.5) + 1) if n % i == 0)
        )
    )
    fkt_list = sorted(fkt)
    return [i for i in fkt_list if i < 1000]


# OBE
def r_ij(m, baris_i, baris_j, r):
    return m[baris_i] + r * m[baris_j]


# tukar
def tukar(m, baris_i, baris_j):
    m[baris_i] = m[baris_i] + m[baris_j]
    m[baris_j] = m[baris_i] - m[baris_j]
    m[baris_i] = m[baris_i] - m[baris_j]


# barisan logistic map
def log(x0, banyak):
    x = x0
    for i in range(1000):
        x = 3.9 * x * (1 - x)

    barisan = np.zeros(banyak, dtype=np.uint8)
    for i in range(banyak):
        x = 3.9 * x * (1 - x)
        barisan[i] = x * 1000 % 256
    return barisan


# membuat kunci
def kunci(n, x0):
    # matriks segitiga atas
    banyak = int(n * (n - 1) / 2)
    barisan = log(x0, banyak + n - 1)

    msa = np.eye(n)

    indeks = 0
    for i in range(n):
        for j in range(i + 1, n):
            msa[i, j] = barisan[indeks]
            indeks += 1
            # ~ print msa
            # ~ print

    for baris_i in range(1, n):
        msa[baris_i] = r_ij(msa, baris_i, 0, barisan[indeks]) % 256
        indeks += 1
        # ~ print msa
        # ~ print '#'*20

    augmented = np.zeros((n, 2 * n))
    augmented[:, :n] = msa

    augmented[:, n:] = np.eye(n)
    # ~ print augmented

    # OBE untuk dapatkan invers
    # mengenolkan segitiga bawah
    for kolom in range(n):
        for baris in range(kolom + 1, n):
            # ~ print baris, kolom
            augmented[baris] = (
                r_ij(augmented, baris, kolom, -augmented[baris, kolom]) % 256
            )
            # ~ print augmented.astype(np.uint8)
            # ~ print

    # mengenolkan segitiga atas
    for kolom in range(1, n):
        for baris in range(kolom):
            # ~ print baris, kolom
            augmented[baris] = (
                r_ij(augmented, baris, kolom, -augmented[baris, kolom]) % 256
            )
            # ~ print augmented.astype(np.uint8)
            # ~ print

    mbalik = augmented[:, n:]
    # ~ print mbalik
    # ~ # Cek perkaliannya
    # ~ print np.dot(msa, mbalik)%256

    return msa, mbalik


"""Fungsi Enkripsi UHC"""


# enkripsi gambar dengan uhc
def enkripsi_uhc(gb, ukuran, x0):
    print("=" * 50)
    print("Encryption process begin.")
    gbku = Image.open(gb)
    mgb = np.array(gbku)
    # if mgb.ndim > 2:
    #    mgb = mgb[:,:,:3]
    # gbku.show()
    # print mgb

    kunciku, balikku = kunci(ukuran, x0)

    print(ukuran, mgb.size, mgb.size / 2)
    mgb_reshape = mgb.reshape((ukuran, int(mgb.size / ukuran)))

    m_kali = np.dot(kunciku, mgb_reshape) % 256
    m_chiper = m_kali.reshape(mgb.shape).astype(np.uint8)

    # ~ print kunciku
    # ~ print mgb_reshape
    # ~ print m_chiper
    # save to image
    img = Image.fromarray(m_chiper)
    img.save("enkripsi_uhc.png")

    print("-----------------------------------------------------------------")
    password2 = str(x0)
    pjgx0 = len(password2)
    password2 = password2[2 : pjgx0 - 1]
    print("Please remember your two-layer password:")
    print("Password 1:", ukuran)
    print("Password 2:", password2)
    print("-----------------------------------------------------------------")
    print("Encryption process is done.")


"""Dekripsi Gambar Dengan UHC"""


# dekripsi gambar dengan uhc
def dekripsi_uhc(gb, ukuran, x0):
    print("Decryption process begin.")

    gbku = Image.open(gb)
    mgb = np.array(gbku)

    kunciku, balikku = kunci(ukuran, x0)

    mgb_reshape = mgb.reshape((ukuran, int(mgb.size / ukuran)))

    m_kali = np.dot(balikku, mgb_reshape) % 256
    m_dechiper = m_kali.reshape(mgb.shape).astype(np.uint8)

    dechiper = Image.fromarray(m_dechiper)
    dechiper.save("dekripsi.png")


"""Enkripsi AES"""


# enkripsi dengan AES
def enkripsi_aes(input_file, output_file):
    gb = Image.open(input_file)
    mgb = np.array(gb)
    ukuran = mgb.shape
    print(ukuran)
    print(mgb.size)

    mgb_byte = mgb.tobytes()

    key = get_random_bytes(16)
    iv = get_random_bytes(16)

    with open("key_file", "wb") as f:
        f.write(key)
    with open("iv_file", "wb") as f:
        f.write(iv)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    mgb_byte_padded = pad(mgb_byte, AES.block_size)
    ciphertext = cipher.encrypt(mgb_byte_padded)

    print(f"panjang mgb_byte: {len(mgb_byte)}")
    print(f"panjang mgb_byte_padded: {len(mgb_byte_padded)}")
    print(f"panjang ciphertext: {len(ciphertext)}")

    # simpan file
    np_cipher = np.frombuffer(ciphertext, dtype=mgb.dtype)
    np_cipher = np_cipher[: mgb.size]
    np_cipher_reshape = np_cipher.reshape(ukuran)
    gb_cipher = Image.fromarray(np_cipher_reshape)
    gb_cipher.save(output_file)

    print("file iv dan key ada di: iv_file dan key_file")


"""Dekripsi AES"""


# dekripsi dengan AES
def dekripsi_aes(input_file, output_file, iv, key):
    gb = Image.open(input_file)
    mgb = np.array(gb)
    ukuran = mgb.shape
    print(ukuran)
    print(mgb.size)

    mgb_byte = mgb.tobytes()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    mgb_byte_padded = pad(mgb_byte, AES.block_size)
    decrypted_byte = cipher.decrypt(mgb_byte_padded)

    print(f"panjang mgb_byte: {len(mgb_byte)}")
    print(f"panjang mgb_byte_padded: {len(mgb_byte_padded)}")
    print(f"panjang ciphertext: {len(decrypted_byte)}")

    # simpan file
    np_decrypted = np.frombuffer(decrypted_byte, dtype=mgb.dtype)
    np_decrypted = np_decrypted[: mgb.size]
    np_decrypted_reshape = np_decrypted.reshape(ukuran)
    gb_decrypted = Image.fromarray(np_decrypted_reshape)
    gb_decrypted.save(output_file)


"""Fungsi Enkripsi Utama (UCH+AES)"""


def main_encrypt(original):
    print("-------------------------")
    print("You will encrypt an image")
    print("-------------------------")
    print
    gb = original
    gbku = Image.open(gb)
    mgb = np.array(gbku)
    ukuran = mgb.size
    faktor = factors(ukuran)

    key = get_random_bytes(16)
    save_key_to_file(key, "key_file")
    iv = get_random_bytes(16)
    save_key_to_file(iv, "iv_file")

    # print ukuran
    # print
    print(
        "----------------------------------------------------------------------------"
    )
    print(faktor)
    print(
        "----------------------------------------------------------------------------"
    )

    password1 = int(
        input("Please choose one of the numbers in the set above as Password 1:")
    )
    # print password1
    while int(password1) not in faktor:
        print("Your choice are ", password1)
        print("Not in the given list.")
        print("-" * 50, "\nThe list of numbers are:")
        print(faktor)
        password1 = input("Please choose again the right one:")
    print("Your Password 1 is: ", password1, "\n")
    pw2 = int(
        input(
            "Enter Password 2 in the form of a number, maximum 14 digits (example: 22021985)\nPassword 2:"
        )
    )
    print("Your Password 2 is: ", pw2)
    password2 = float("0." + str(pw2) + "1")

    # proses enkripsi dimulai
    waktu_mulai = time.time()
    enkripsi_uhc(gb, password1, password2)
    waktu_selesai_uhc = time.time()
    waktu_enkripsi_uhc = waktu_selesai_uhc - waktu_mulai
    print("Waktu enkripsi UHC: ", waktu_enkripsi_uhc, "detik")

    # encrypt the chiper image with AES
    enkripsi_aes("enkripsi_uhc.png", "enkripsi_uhc_aes.png")
    waktu_selesai_aes = time.time()
    waktu_enkripsi_aes = waktu_selesai_aes - waktu_selesai_uhc
    print("Waktu enkripsi AES: ", waktu_enkripsi_aes, "detik")


"""Fungsi Dekripsi Utama (UHC+AES)"""


def main_decrypt(encrypted):
    print("*" * 80)
    print(
        "Dekripsi Gambar digital dengan memanfaatkan matriks unimodular dan fungsi chaos logistic map"
    )
    print("-" * 50)

    # gb_encrypted = input("Now, insert your encrypted image with its extension (example: image.png):")
    gb_encrypted = encrypted

    with open("key_file", "rb") as f:
        key = f.read()
    with open("iv_file", "rb") as f:
        iv = f.read()

    gb_decrypted = "dekripsi_uhc_aes.png"
    waktu_mulai = time.time()
    dekripsi_aes(gb_encrypted, gb_decrypted, iv, key)
    waktu_selesai_aes = time.time()
    waktu_dekripsi_aes = waktu_selesai_aes - waktu_mulai
    print("Waktu dekripsi AES: ", waktu_dekripsi_aes, "detik")

    gbku = Image.open(gb_decrypted)
    mgb = np.array(gbku)
    ukuran = mgb.size
    faktor = sorted(factors(ukuran))

    # print ukuran
    print(
        "----------------------------------------------------------------------------"
    )
    print(faktor)
    print(
        "----------------------------------------------------------------------------"
    )

    password1 = int(
        input("Please choose one of the numbers in the set above as Password 1:")
    )
    # print password1
    while password1 not in faktor:
        print("Your choice are ", password1)
        print("Not in the given list.")
        print("-" * 50, "\nThe list of numbers are:")

        password1 = input("Please choose again the right one:")
    print("Your Password 1 is: ", password1, "\n")
    pw2 = int(
        input(
            "Enter Password 2 in the form of a number, maximum 14 digits (example: 22021985)\nPassword 2:"
        )
    )
    print("Your Password 2 is: ", pw2)
    password2 = float("0." + str(pw2) + "1")

    # proses dekripsi dimulai
    waktu_mulai = time.time()
    dekripsi_uhc(gb_decrypted, password1, password2)
    waktu_selesai_uhc = time.time()
    waktu_dekripsi_uhc = waktu_selesai_uhc - waktu_mulai
    print("Waktu dekripsi UHC: ", waktu_dekripsi_uhc, "detik")


"""Fungsi Membuat Histogram"""


def create_histogram(image_path):
    # Buka gambar
    img = Image.open(image_path)

    # Konversi gambar menjadi array numpy
    img_array = np.array(img)

    # Jika gambar memiliki 3 kanal (RGB), pisahkan setiap kanal
    if len(img_array.shape) == 3:
        # Pisahkan kanal R, G, dan B
        r, g, b = img_array[:, :, 0], img_array[:, :, 1], img_array[:, :, 2]

        # Buat histogram untuk setiap kanal
        fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True, sharey=True)

        axs[0].hist(r.flatten(), bins=256, color="red", alpha=0.5)
        axs[0].set_title("Red Channel")

        axs[1].hist(g.flatten(), bins=256, color="green", alpha=0.5)
        axs[1].set_title("Green Channel")

        axs[2].hist(b.flatten(), bins=256, color="blue", alpha=0.5)
        axs[2].set_title("Blue Channel")

        plt.xlabel("Pixel Intensity")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig("histogram_sebaran_huruf.png")
        plt.show()

    # Jika gambar grayscale
    else:
        plt.hist(img_array.flatten(), bins=256, color="gray", alpha=0.5)
        plt.title("Grayscale Channel")
        plt.xlabel("Pixel Intensity")
        plt.ylabel("Frequency")
        plt.show()


"""Fungsi Menghitung Jaccard Similarity"""


def image_to_set(image_path):
    img = Image.open(image_path).convert("L")  # Konversi gambar menjadi grayscale
    img_array = np.array(img)
    return set(map(tuple, img_array))


def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    res = intersection / union
    print(f"Jaccard Similarity antara gambar original dan hasil enkripsi: {res:.4f}")


"""Fungsi Analisis Entropy"""


def calculate_entropy(image_path):
    # Buka gambar dan konversi ke grayscale
    img = Image.open(image_path).convert("L")
    img_array = np.array(img)

    # Hitung histogram dari gambar
    histogram, _ = np.histogram(img_array, bins=256, range=(0, 256))

    # Normalisasi histogram sehingga jumlah totalnya adalah 1
    histogram = histogram / histogram.sum()

    # Hitung entropi
    ent = entropy(histogram, base=2)
    print(f"Entropi dari gambar {image_path}: {ent:.4f}")


"""Main Menu dan Function"""

menu_options = {
    1: "Encryption",
    2: "Decryption",
    3: "Original Histogram and Frequency Analysis",
    4: "Encrypted Histogram and Frequency Analysis",
    5: "Jaccard Similarity",
    6: "Entropy Analisys",
    7: "Exit",
}

print("============================================================================")
print("Digital Image Encryption Algorithm Trough UHC and AES")
print("============================================================================")


def print_menu():
    for key in menu_options.keys():
        print(key, "--", menu_options[key])


if __name__ == "__main__":
    while True:
        print_menu()
        option = ""
        try:
            option = int(input("Enter your choice: "))
        except:
            print("Wrong input. Please enter a number ...")
        if option == 1:
            main_encrypt("gambar.png")
            print(
                "Ukuran file 20original sebesar ",
                os.stat("gambar.png").st_size / 1024,
                "kilobytes",
            )
            print(
                "Ukuran file enkripsi uhc sebesar ",
                os.stat("enkripsi_uhc.png").st_size / 1024,
                "kilobytes",
            )
            print(
                "Ukuran file enkripsi uhc+aes sebesar ",
                os.stat("enkripsi_uhc_aes.png").st_size / 1024,
                "kilobytes",
            )
        elif option == 2:
            main_decrypt("enkripsi_uhc_aes.png")
        elif option == 3:
            create_histogram("gambar.png")
        elif option == 4:
            create_histogram("enkripsi_uhc_aes.png")
        elif option == 5:
            jaccard_similarity(
                image_to_set("gambar.png"), image_to_set("enkripsi_uhc.png")
            )
            jaccard_similarity(
                image_to_set("gambar.png"), image_to_set("enkripsi_uhc_aes.png")
            )
        elif option == 6:
            calculate_entropy("gambar.png")
            calculate_entropy("enkripsi_uhc.png")
            calculate_entropy("enkripsi_uhc_aes.png")
        elif option == 7:
            print("Thank you for using this program. Please press enter")
            quit()
            exit()
        else:
            print("Invalid option. Please enter a number between 1 and 7.")
            quit()
            break
