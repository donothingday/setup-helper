import subprocess
import re
import shlex
import sys
import shutil
import msvcrt

def jalankan_perintah(cmd):
    try:
        # AMAN: gunakan list instead of shell=True
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        hasil = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
        return hasil.stdout
    except Exception as e:
        return str(e)

def ambil_input_atau_esc(prompt_text):
    print(prompt_text, end="", flush=True)
    input_str = ""
    while True:
        char = msvcrt.getch()
        if char == b'\x1b':
            print()
            return "ESC"
        elif char == b'\r':
            print()
            return input_str.strip()
        elif char == b'\x08':
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


def pilih_software(target_apps):
    while True:
        print("\n" + "=" * 70)
        print(f"{'PILIH SOFTWARE UNTUK CEK VERSI':^70}")
        print("=" * 70)
        print("\nKetik kata kunci untuk cari")
        print("Pilih beberapa nomor pisah koma, contoh: 2,5,9")
        print("Tekan ESC untuk keluar")
        print("Tekan enter untuk lanjut")
        print()
        
        search = ambil_input_atau_esc("Cari software: ")
        if search == "ESC":
            return []
        
        query = search.strip().lower()
        daftar = [app for app in target_apps if query in app.lower()] if query else target_apps
        if not daftar:
            print("\n❌ Tidak ada software yang cocok.")
            input("👉 Tekan Enter untuk kembali...")
            continue
        
        print("\nHasil pencarian:")
        for i, app in enumerate(daftar, 1):
            print(f"{i:2d}. {app}")
        
        pilih = ambil_input_atau_esc("\nPilih nomor (contoh: 3,20,3): ")
        if pilih == "ESC":
            return []
        
        hasil = []
        for part in re.split(r'[\s,]+', pilih.strip()):
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(daftar):
                    hasil.append(daftar[idx])
        if hasil:
            print("\nYang dipilih:")
            for app in hasil:
                print(f"- {app}")
            return hasil
        print("\n❌ Tidak ada pilihan yang valid.")
        input("👉 Tekan Enter untuk kembali...")


def cek_di_path(app):
    """Cek apakah software tersedia di PATH dan ambil versinya"""
    version_commands = {
        "java": ["java", "--version"],
        "python": ["python", "--version"],
        "npm": ["npm", "--version"],
        "node": ["node", "--version"],
        "git": ["git", "--version"],
        "ruby": ["ruby", "--version"],
        "go": ["go", "version"],
        "rust": ["rustc", "--version"],
        "php": ["php", "--version"],
        "curl": ["curl", "--version"],
        "docker": ["docker", "--version"],
        "kubectl": ["kubectl", "version", "--client"],
        "composer": ["composer", "--version"]
    }
    
    if app in version_commands:
        cmd = version_commands[app]
        # AMAN & FIX: cari path asli executable (handle .cmd/.bat di Windows, misal npm)
        exe = shutil.which(cmd[0])
        if not exe:
            return None
        try:
            result = subprocess.run([exe] + cmd[1:], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=5)
            if result.returncode == 0:
                # Ambil baris pertama output
                versi = result.stdout.split('\n')[0][:15]
                return versi
        except:
            pass
    return None

def cek_latest_version_npm():
    try:
        result = subprocess.run(["npm", "view", "npm", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def cek_status_software(target_apps=None):
    print("=" * 70)
    print(f"{'NAMA PACKAGE':<25} {'VERSI SEKARANG':<15} {'VERSI TERBARU':<15} {'STATUS':<10}")
    print("=" * 70)
    
    # Mengambil list software yang butuh update dari winget
    data_winget = jalankan_perintah(["winget", "upgrade"])
    
    # Keyword software yang ingin kamu pantau khusus
    if target_apps is None:
        target_apps = [
            "java", "apache", "node", "python", "git",  # yang sudah ada
            
            # Development Tools
            "visual studio code",    # Visual Studio Code (nama sesuai winget)
            "docker",                # Docker Desktop
            "git-lfs",               # Git Large File Storage
            
            # Databases
            "postgresql",            # PostgreSQL
            "mysql",                 # MySQL Server
            "mongodb",               # MongoDB
            
            # Programming Languages
            "golang",                # Go
            "rust",                  # Rust
            "ruby",                  # Ruby
            ".net",                  # .NET Runtime
            "php",                   # PHP
            
            # Build Tools & Package Managers
            "gradle",                # Gradle
            "maven",                 # Maven
            
            # DevOps & Infrastructure
            "terraform",             # Terraform
            "kubectl",               # Kubernetes CLI
            
            # Utilities
            "7zip",                  # 7-Zip
            "curl",                  # cURL
            "ffmpeg",                # FFmpeg
            "putty",                 # PuTTY SSH Client
        ]
    
    lines = data_winget.split('\n') if data_winget else []
    
    for app in target_apps:
        # AMAN: Validasi input dengan whitelist
        if not re.match(r'^[a-zA-Z0-9\-_.]+$', app):
            continue
            
        ditemukan = False
        for line in lines:
            # Cocokkan nama aplikasi (case-insensitive)
            if re.search(r'\b' + re.escape(app) + r'\b', line, re.IGNORECASE):
                # Split baris berdasarkan multiple spaces
                parts = re.split(r'\s{2,}', line.strip())
                if len(parts) >= 4:
                    nama = parts[0]
                    versi_skrg = parts[2]
                    versi_baru = parts[3]
                    print(f"{nama:<25} {versi_skrg:<15} {versi_baru:<15} {'UPDATE!!':<10}")
                    ditemukan = True
                    break
        
        # Jika tidak ada di daftar update winget, cek apakah aslinya terinstall (Up to Date)
        if not ditemukan:
            cek_install = jalankan_perintah(["winget", "list", "--name", app])
            if cek_install and app in cek_install.lower():
                # Ambil versi terinstall saat ini
                for cl in cek_install.split('\n'):
                    if re.search(r'\b' + re.escape(app) + r'\b', cl, re.IGNORECASE):
                        parts = re.split(r'\s{2,}', cl.strip())
                        if len(parts) >= 3:
                            print(f"{parts[0]:<25} {parts[2]:<15} {parts[2]:<15} {'UPDATED':<10}")
                            ditemukan = True
                            break
            
            # Jika belum ditemukan, cek di PATH
            if not ditemukan:
                versi_path = cek_di_path(app)
                if versi_path:
                    if app.lower() == "npm":
                        latest_version = cek_latest_version_npm()
                        print(f"{app.upper():<25} {versi_path:<15} {latest_version or '-':<15} {'INSTALLED':<10}")
                    else:
                        print(f"{app.upper():<25} {versi_path:<15} {'-':<15} {'INSTALLED':<10}")
                    ditemukan = True
            
            if not ditemukan:
                print(f"{app.upper():<25} {'Belum Install':<15} {'-':<15} {'-':<10}")


def jalankan_cek_versi():
    """Entry point biar bisa dipanggil langsung (import) dari main.py, tanpa subprocess"""
    target_apps = [
        "java", "apache", "node", "python", "npm", "git",
        "visual studio code", "docker", "git-lfs",
        "postgresql", "mysql", "mongodb",
        "golang", "rust", "ruby", ".net", "php",
        "gradle", "maven", "terraform", "kubectl",
        "7zip", "curl", "ffmpeg", "putty"
    ]
    selected_apps = pilih_software(target_apps)
    if selected_apps:
        cek_status_software(selected_apps)
    print("=" * 70)


if __name__ == "__main__":
    jalankan_cek_versi()
