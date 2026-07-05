import subprocess
import sys
import re
import msvcrt
import os
import shutil

PACKAGE_MAP = {
    "java": "Eclipse.Temurin.JDK.21",
    "node": "OpenJS.NodeJS",
    "python": "Python.Python.3.11",
    "npm": "OpenJS.NodeJS",
    "git": "Git.Git",
    "visual studio code": "Microsoft.VisualStudioCode",
    "docker": "Docker.DockerDesktop",
    "git-lfs": "GitHub.GitLFS",
    "postgresql": "PostgreSQL.PostgreSQL",
    "mysql": "MySQL.MySQL",
    "mongodb": "MongoDB.MongoDB",
    "golang": "GoLang.Go",
    "rust": "Rustlang.Rust.GNU",
    "ruby": "RubyInstallerTeam.Ruby",
    ".net": "Microsoft.DotNet.DesktopRuntime.8",
    "php": "PHP.PHP",
    "gradle": "Gradle.Gradle",
    "maven": "Apache.Maven",
    "terraform": "HashiCorp.Terraform",
    "kubectl": "Kubernetes.kubectl",
    "7zip": "7zip.7zip",
    "curl": "cURL.cURL",
    "ffmpeg": "FFmpeg.FFmpeg",
    "putty": "PuTTY.PuTTY",
}

SOFTWARE_LIST = list(PACKAGE_MAP.keys())

def jalankan_perintah(cmd):
    try:
        if isinstance(cmd, str):
            cmd = [cmd]
        hasil = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return hasil.stdout
    except Exception as e:
        return str(e)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def cek_software_installed(software):
    if software in {"node", "npm"}:
        return shutil.which("node") is not None or shutil.which("npm") is not None

    package_id = PACKAGE_MAP.get(software)
    if package_id:
        try:
            result = subprocess.run(
                ["winget", "list", "--id", package_id],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            output = (result.stdout + result.stderr).lower()
            return package_id.lower() in output or software.lower() in output
        except:
            pass

    try:
        result = subprocess.run(
            ["winget", "list", "--name", software],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10
        )
        output = (result.stdout + result.stderr).lower()
        return software.lower() in output
    except:
        return False

def ambil_input_atau_esc(prompt_text):
    """Fungsi biar bisa ngetik nomor + Enter, tapi kalau pencet ESC langsung batal"""
    print(prompt_text, end="", flush=True)
    input_str = ""
    while True:
        char = msvcrt.getch()
        if char == b'\x1b': # Tombol ESC ditekan
            print()
            return "ESC"
        elif char == b'\r': # Tombol Enter ditekan
            print()
            return input_str.strip()
        elif char == b'\x08': # Tombol Backspace ditekan
            if len(input_str) > 0:
                input_str = input_str[:-1]
                sys.stdout.write('\b \b')
                sys.stdout.flush()
        else:
            try:
                ch_decoded = char.decode('utf-8')
                if ch_decoded.isalnum() or ch_decoded in ".,-_ ":
                    input_str += ch_decoded
                    sys.stdout.write(ch_decoded)
                    sys.stdout.flush()
            except:
                pass

def tampilkan_submenu_install_hapus(software):
    clear_screen()
    print("\n" + "=" * 70)
    print(f"PILIHAN UNTUK: {software.upper()}")
    print("=" * 70)
    
    is_installed = cek_software_installed(software)
    
    if is_installed:
        print(f"\n✅ {software} sudah terinstall")
        print("\nOpsi:")
        print("1. Re-install")
        print("2. Hapus (Uninstall)")
        print("3. Kembali (ESC)\n")
    else:
        print(f"\n⬜ {software} belum terinstall")
        print("\nOpsi:")
        print("1. Install")
        print("2. Kembali (ESC)\n")
    
    print("=" * 70)
    pilihan = ambil_input_atau_esc("Pilih opsi: ")
    
    if pilihan == "ESC":
        return "3" if is_installed else "2", is_installed
        
    return pilihan, is_installed

def install_single_software(software):
    package_id = PACKAGE_MAP.get(software)
    if not package_id:
        print(f"❌ Package ID untuk {software} tidak ditemukan!")
        input("👉 Tekan Enter untuk kembali...")
        return False
    
    print(f"\n⏳ Menginstall {software}...\n")
    try:
        result = subprocess.run(
            ["winget", "install", package_id, "--accept-package-agreements", "--accept-source-agreements"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"✅ {software} berhasil diinstall!")
        else:
            print(f"⚠️  {software} mungkin sudah terinstall atau ada error.")
    except subprocess.TimeoutExpired:
        print(f"⏱️  {software} timeout (mungkin masih download).")
    except Exception as e:
        print(f"❌ Error installing {software}: {str(e)}")
    
    input("👉 Tekan Enter untuk kembali...")

def hapus_software(software):
    package_id = PACKAGE_MAP.get(software, software)
    print(f"\n⚠️  Anda akan menghapus {software}")
    confirm = input("Lanjutkan? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Dibatalkan.")
        input("👉 Tekan Enter untuk kembali...")
        return
    
    print(f"\n⏳ Menghapus {software}...\n")
    try:
        result = subprocess.run(
            ["winget", "uninstall", package_id, "--accept-source-agreements"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print(f"✅ {software} berhasil dihapus!")
        else:
            print(f"⚠️  {software} tidak ditemukan atau ada error.")
    except subprocess.TimeoutExpired:
        print(f"⏱️  {software} timeout.")
    except Exception as e:
        print(f"❌ Error menghapus {software}: {str(e)}")
    
    input("👉 Tekan Enter untuk kembali...")

def tampilkan_list_software():
    while True:
        clear_screen()
        print("\n" + "=" * 70)
        print(f"{'PILIH SOFTWARE UNTUK DIINSTALL':^70}")
        print("=" * 70)
        print()
        print("Ketik kata kunci untuk cari")
        print("Pilih beberapa nomor pisah koma, contoh: 2,5,9")
        print("Tekan ESC untuk keluar")
        print("Tekan enter untuk lanjut")
        print()
        
        search = ambil_input_atau_esc("Cari software: ")
        if search == "ESC":
            break
        
        query = search.strip().lower()
        daftar = [s for s in SOFTWARE_LIST if query in s.lower()] if query else SOFTWARE_LIST
        
        if not daftar:
            print("\n❌ Tidak ada software yang cocok.")
            input("👉 Tekan Enter untuk kembali...")
            continue
        
        clear_screen()
        print("\nHasil pencarian:")
        for i, software in enumerate(daftar, 1):
            print(f"{i:2d}. {software:<30}")
        
        try:
            nomor_input = ambil_input_atau_esc(f"\nPilih nomor (contoh: 3,20,3): ")
            if nomor_input == "ESC":
                break
            if nomor_input == '':
                continue
            
            pilihan_list = []
            for part in re.split(r'[\s,]+', nomor_input.strip()):
                if part.isdigit():
                    idx = int(part) - 1
                    if 0 <= idx < len(daftar):
                        pilihan_list.append(daftar[idx])
            
            if not pilihan_list:
                print("\n❌ Tidak ada pilihan yang valid.")
                input("👉 Tekan Enter untuk kembali...")
                continue
            
            print("\nYang dipilih:")
            for software in pilihan_list:
                print(f"- {software}")
            
            for software in pilihan_list:
                while True:
                    pilihan, is_installed = tampilkan_submenu_install_hapus(software)
                    
                    if is_installed:
                        if pilihan == '1':
                            install_single_software(software)
                            break
                        elif pilihan == '2':
                            hapus_software(software)
                            break
                        elif pilihan == '3' or pilihan == 'ESC':
                            break
                    else:
                        if pilihan == '1':
                            install_single_software(software)
                            break
                        elif pilihan == '2' or pilihan == 'ESC':
                            break
        except ValueError:
            print("\n❌ Input tidak valid.")
            input("👉 Tekan Enter untuk kembali...")
        except KeyboardInterrupt:
            return False

def main():
    tampilkan_list_software()
    print("\n👋 Kembali ke menu utama.")

if __name__ == "__main__":
    main()
