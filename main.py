import sys
import os
import msvcrt
from pyfiglet import figlet_format

import script
import install


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def tampilkan_menu_utama():
    """Tampilkan menu utama"""
    while True:
        clear_screen()
        print("=" * 127)
        print("=" * 127)
        teks = figlet_format("SETUP HELPER", font="3d_diagonal", width=1000)
        print(teks)
        print("=" * 127)
        print("=" * 127)
        print("\n1. 📊 Lihat Versi Software")
        print("2. ⬇️  Install Software")
        print("\nKetik 1-2, atau tekan ESC untuk keluar\n")
        
        print("Pilih opsi: ", end="", flush=True)
        
        try:
            char = msvcrt.getch()
            
            if char == b'\x1b': 
                print("\n\nThanks kacung.")
                sys.exit(0)
                
            pilihan = char.decode('utf-8', errors='ignore').strip()
            print(pilihan)
            
            if pilihan == "":
                continue
            elif pilihan == "1":
                lihat_versi()
            elif pilihan == "2":
                install_software()
            else:
                print("❌ Opsi tidak valid, silakan coba lagi.")
        except KeyboardInterrupt:
            print("\n\nThanks kacung.")
            sys.exit(0)


def lihat_versi():
    """Panggil langsung fungsi dari script.py (bukan subprocess), biar tetap jalan setelah di-compile ke exe"""
    try:
        script.jalankan_cek_versi()
    except Exception as e:
        print(f"\n❌ Error saat mengecek versi software: {e}")
    
    input("\n👉 Tekan Enter untuk kembali ke menu...")


def install_software():
    """Panggil langsung fungsi dari install.py (bukan subprocess), biar tetap jalan setelah di-compile ke exe"""
    clear_screen()
    try:
        install.main()
    except Exception as e:
        print(f"\n❌ Error saat install software: {e}")
        input("👉 Tekan Enter untuk kembali...")


if __name__ == "__main__":
    tampilkan_menu_utama()
