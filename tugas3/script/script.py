import subprocess
import sys
import os
import shutil
import stat
import time
import pytsk3


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def create_vhd(filename: str, size: str):
    vhd_folder = './vhd'
    vhd_file = f'{vhd_folder}/{filename}.vhd'
    
    if not os.path.exists(vhd_folder):
        os.makedirs(vhd_folder)
        print(f"{Colors.BLUE}[Info]{Colors.RESET} Folder {vhd_folder} berhasil dibuat.")

    cmd = ['qemu-img', 'create', '-f', 'vpc', vhd_file, size]
    
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
        print(f"\n{Colors.GREEN}[Sukses]{Colors.RESET} {filename}.vhd dengan ukuran {size} berhasil dibuat dan disimpan di {vhd_file}")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} Pembuatan VHD gagal: {e.stderr.decode()}")

def attach(path: str, vhd: str):
    try:
        subprocess.run(['sudo', 'modprobe', 'nbd'], check=True)
        print(f"{Colors.GREEN}[Sukses]{Colors.RESET}  Modul nbd dimuat.")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} Gagal memuat modul nbd: {e.stderr.decode()}")
        return

    cmd = ['sudo', 'qemu-nbd', '-n', f'--connect={path}', vhd]

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
        checkDisk = subprocess.run(['sudo','fdisk','-l',path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(checkDisk.stdout.decode())
        print(f"\n{Colors.GREEN}[Sukses]{Colors.RESET} Disk VHD {vhd} terhubung ke {path}.")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} Gagal menghubungkan VHD: {e.stderr.decode()}")

def create_partition(path: str):
    print(f"Mempartisi {path} ...")
    
    partisi_type = input("Pilih jenis partisi (primary/extended): ").strip().lower()
    partisi_number = input("Masukkan nomor partisi (misal: 1): ").strip()
    partisi_size = input("Masukkan ukuran partisi (misal: +100M atau tekan Enter untuk ukuran penuh): ").strip()

    fdisk_commands = [
        'n\n',
        f'{partisi_type[0]}\n',
        f'{partisi_number}\n',
        '\n',
        f'{partisi_size}\n' if partisi_size else '\n',
        'w\n'
    ]

    try:
        process = subprocess.Popen(['sudo', 'fdisk', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        process.communicate(input="".join(fdisk_commands).encode())
        
        output, err = process.communicate()

        if process.returncode == 0:
            print(f"{Colors.GREEN}[Sukses]{Colors.RESET} Partisi pada {path} berhasil dibuat.\n")
            checkDisk = subprocess.run(['sudo','fdisk','-l',path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(checkDisk.stdout.decode())
        else:
            print(f"{Colors.RED}[Error]{Colors.RESET} Partisi gagal: {err.decode()}")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} Gagal membuat partisi: {e.stderr.decode()}")

def format_partition(path, filesystem):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} Memformat {path} dengan sistem file {filesystem}...")

    if filesystem == 'fat32':
        cmd = ['sudo', 'mkfs.fat', '-F', '32', f'{path}']
    elif filesystem == 'ntfs':
        cmd = ['sudo', 'mkfs.ntfs', f'{path}']
    elif filesystem == 'ext4':
        cmd = ['sudo', 'mkfs.ext4', f'{path}']
    else:
        print(f"{Colors.RED}[Error]{Colors.RESET} Sistem file {filesystem} tidak dikenali. Harap pilih antara 'fat32', 'ntfs', atau 'ext4'.")
        return

    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())
        print(f"{Colors.GREEN}[Sukses]{Colors.RESET} Partisi {path}p1 berhasil diformat dengan sistem file {filesystem}.")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} Gagal memformat partisi: {e.stderr.decode()}")

def calculate_hash(vhd_path: str):
    try:
        result = subprocess.run(['md5sum', vhd_path], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        hash_md5 = result.stdout.split()[0]
        
        print(f"{Colors.BLUE}[Info]{Colors.RESET} MD5 hash dari {vhd_path}: {hash_md5}")
        return hash_md5

    except FileNotFoundError:
        print(f"{Colors.RED}[Error]{Colors.RESET} File VHD {vhd_path} tidak ditemukan.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} Gagal menghitung MD5 hash: {e.stderr}")
        return None

def calculate_diff(hash1_file: str, hash2_file: str):
    try:
        result = subprocess.run(['diff', hash1_file, hash2_file], capture_output=True, text=True)

        if result.returncode == 0:
            print(f"{Colors.GREEN}[Info]{Colors.RESET} Hashes are identical.")
            return True
        elif result.returncode == 1:
            print(f"{Colors.RED}[Warning]{Colors.RESET} Hashes are different.")
            print(result.stdout)
            return False
        else:
            print(f"{Colors.RED}[Error]{Colors.RESET} Error occurred while comparing files.")
            print(result.stderr)
            return None

    except FileNotFoundError as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} File tidak ditemukan: {e.filename}")
        return None
    except Exception as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} Terjadi kesalahan: {e}")
        return None

def create_files_in_vhd(mount_path : str, num_files : str):
    print(f"{Colors.BLUE}[Info]{Colors.RESET} Membuat {num_files} file di {mount_path} ...")
    try:
        for i in range(num_files):
            file_path = os.path.join(mount_path, f"file_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Ini adalah file nomor {i}\n")
        print(f"{Colors.GREEN}[Sukses]{Colors.RESET} File berhasil dibuat.")
    except Exception as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} Gagal membuat file: {e}")

def delete_files_in_vhd(mount_path : str, num_files : str):
    print(f"{Colors.BLUE}[Info]{Colors.RESET} Menghapus {num_files} file dari {mount_path} ...")
    try:
        for i in range(num_files):
            file_path = os.path.join(mount_path, f"file_{i}.txt")
            if os.path.exists(file_path):
                os.remove(file_path)
            else:
                print(f"{Colors.RED}[Warning]{Colors.RESET} File {file_path} tidak ditemukan.")
        print(f"{Colors.GREEN}[Sukses]{Colors.RESET} File berhasil dihapus.")
    except Exception as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} Gagal menghapus file: {e}")

def mount(nbd_path: str, mount_point: str):
    user = os.getenv('USER')
    mount_point = f"/home/{user}{mount_point}"

    if not os.path.exists(mount_point):
        os.makedirs(mount_point)
        print(f"{Colors.BLUE}[Info]{Colors.RESET} Mount point {mount_point} created.")

    uid = os.getuid()
    gid = os.getgid()

    try:
        filesystem_type = subprocess.check_output(['blkid', '-s', 'TYPE', nbd_path]).decode().strip()
        
        if 'TYPE="ext4"' in filesystem_type:
            print(f"{Colors.BLUE}[Info]{Colors.RESET} Attempting to mount as ext4...")
            subprocess.run(['sudo', 'mount', '-t', 'ext4', nbd_path, mount_point],check=True)
            subprocess.run(['sudo', 'chown', '-R', f'{uid}:{gid}', mount_point], check=True)
            subprocess.run(['sudo', 'chmod', '777', mount_point], check=True)
        else:
            print(f"{Colors.BLUE}[Info]{Colors.RESET} Mounting with auto-detecting filesystem type...")
            subprocess.run(['sudo', 'mount', nbd_path, mount_point, '-o', f'uid={uid},gid={gid},umask=0022'], check=True)

        print(f"{Colors.BLUE}[Info]{Colors.RESET} {nbd_path} mounted to {mount_point}.")
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} Failed to mount {nbd_path} to {mount_point}: {e}")
    except Exception as e:
        print(f"{Colors.RED}[Error]{Colors.RESET} An error occurred: {e}")

def unmount(mount_point: str):
    mount_point = f"/home/{os.getenv('USER')}{mount_point}"

    try:
        subprocess.run(['sudo', 'umount', mount_point], check=True)
        print(f"{Colors.GREEN}[Sukses]{Colors.RESET} {mount_point} unmounted successfully.")
        
        if os.path.exists(mount_point):
            shutil.rmtree(mount_point) 
            print(f"{Colors.GREEN}[Sukses]{Colors.RESET} {mount_point} removed successfully.")
        else:
            print(f"{Colors.RED}[Error]{Colors.RESET} {mount_point} does not exist, skipping removal.")

    except subprocess.CalledProcessError as e:
        print(f"Failed to unmount {mount_point}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

def AnalyzeFileSystem(device_path, filename):
    fsstat_dir = './analize/fsstat/'
    fls_dir = './analize/fls/'
    
    os.makedirs(fsstat_dir, exist_ok=True)
    os.makedirs(fls_dir, exist_ok=True)
    
    fsstat_file_path = os.path.join(fsstat_dir, f'{filename}.txt')
    fls_file_path = os.path.join(fls_dir, f'{filename}.txt')

    results = {
        'fsstat_file': fsstat_file_path,
        'fls_file': fls_file_path
    }
    
    try:
        with open(fsstat_file_path, 'w') as fsstat_file:
            fsstat_output = subprocess.check_output(['sudo', 'fsstat', device_path], stderr=subprocess.STDOUT)
            fsstat_file.write(fsstat_output.decode('utf-8'))
        
        with open(fls_file_path, 'w') as fls_file:
            fls_output = subprocess.check_output(['sudo', 'fls', '-r', device_path], stderr=subprocess.STDOUT)
            fls_file.write(fls_output.decode('utf-8'))

        print(f"{Colors.GREEN}[Sukses]{Colors.RESET} : Berhasil menulis output ke {fsstat_file_path} dan {fls_file_path}")

    except subprocess.CalledProcessError as e:
        error_message = e.output.decode('utf-8')
        print(f"{Colors.RED}[Error]{Colors.RESET} An error occurred: {e}")
        results['error'] = error_message

    return results

def main():
    if len(sys.argv) > 1:
        operasi = sys.argv[1]
        
        if operasi in ['-h', '--help']:
            command_list = """
            Script ini digunakan untuk melakukan simulasi tugas dari modul 3
            Studi Independen Analis Forensik Digital.

            List Operasi:
                -c, --create                     : Operasi untuk membuat virtual disk
                -a, --attach                     : Operasi untuk menghubungkan virtual disk ke NBD
                -f, --format                     : Operasi untuk melakukan format partisi dengan file system (fat32, ntfs, ext4)
                -p, --partition                  : Operasi untuk membuat partisi pada disk
                -t, --test                       : Operasi untuk melakukan hash dan file operations
                -m, --mount                      : Operasi untuk melakukan mounting nbd ke mountpoint
                -afs, --analize-file-system      : Operasi untuk melakuakan analisis file system

            Contoh penggunaan:
                python3 script.py -c <filename> <size>
                python3 script.py -a <attaching_path> <vhd>
                python3 script.py -p <path>
                python3 script.py -f <path> <filesystem>
                python3 script.py -t <mounting_path> <vhd>
                python3 script.py -m <nbd_path> <mount_point>
                python3 script.py -afs <device_path> <filename>

            Size :
                <angka>G   : Giga Bytes
                <angka>M   : Mega Bytes

            File System:
                fat32, ntfs, ext4

            Copyright : Indra_Arsana_ [instagram]
            """
            print(command_list)
        elif operasi in ['-c', '--create']:
            if len(sys.argv) != 4:
                print(f"{Colors.RED}[Error]{Colors.RESET} Harap berikan nama file dan ukuran VHD. Usage: python3 script.py -c <filename> <size>")
                return
            
            filename = sys.argv[2]
            size = sys.argv[3]
            create_vhd(filename, size)
        elif operasi in ['-a', '--attach']:
            if len(sys.argv) != 4:
                print(f"{Colors.RED}[Error]{Colors.RESET} Harap berikan path untuk attaching dan file VHD. Usage: python3 script.py -a <attaching_path> <vhd>")
                return
            
            attaching = sys.argv[2]
            vhd_file = sys.argv[3]
            attach(attaching, vhd_file)
        elif operasi in ['-m', '--mount']:
            if len(sys.argv) != 4:
                print(f"{Colors.RED}[Error]{Colors.RESET} Harap berikan path nbd dan mount point. Usage: python3 script.py -m <nbd_path> <mount_point>")
                return
            
            nbd_path = sys.argv[2]
            mount_point = sys.argv[3]
            mount(nbd_path, mount_point)
        elif operasi in ['-u', '--unmount']:
            if len(sys.argv) != 3:
                print(f"{Colors.RED}[Error]{Colors.RESET} Harap berikan path mount point. Usage: python3 script.py -u <mount_point>")
                return
            
            mount_point = sys.argv[2]
            unmount(mount_point)
        elif operasi in ['-p', '--partition']:
            if len(sys.argv) != 3:
                print(f"{Colors.RED}[Error]{Colors.RESET} Harap berikan path ke disk yang ingin dipartisi. Usage: python3 script.py -p <path>")
                return

            disk_path = sys.argv[2]
            create_partition(disk_path)
        elif operasi in ['-f', '--format']:
            if len(sys.argv) != 4:
                print(f"{Colors.RED}[Error]{Colors.RESET} Harap berikan path ke partisi dan tipe sistem file yang diinginkan. Usage: python3 script.py -f <path> <filesystem>")
                return
            
            partition_path = sys.argv[2]
            filesystem = sys.argv[3]
            format_partition(partition_path, filesystem)
        elif operasi in ['-t', '--test']:
            if len(sys.argv) != 4:
                print(f"{Colors.RED}[Error]{Colors.RESET} Harap berikan path untuk mounting dan file VHD. Usage: python3 script.py -t <mounting_path> <vhd>")
                return
            
            mounting_path = f"/home/{os.getenv('USER')}" + sys.argv[2]
            vhd_file = sys.argv[3]

            if os.path.exists(vhd_file):
                mounted = os.path.exists(mounting_path)
                if mounted:
                    try:
                        initial_hash = calculate_hash(vhd_file)

                        if initial_hash is None:
                            print(f"{Colors.RED}[Error]{Colors.RESET} hashing error.")
                            return
                
                        file_path = vhd_file[6:].split('.')[0]

                        if not os.path.exists('./hash/initial/'):
                            os.makedirs('./hash/initial/')
                            print(f"{Colors.BLUE}[Info]{Colors.RESET} Folder './hash/initial/' berhasil dibuat.")

                        with open(f'./hash/initial/{file_path}.txt', 'w') as f:
                            f.write(initial_hash)
                            f.close()

                        create_files_in_vhd(mounting_path, 10)

                        subprocess.run(['sync'])

                        after_creation = calculate_hash(vhd_file)

                        if not os.path.exists('./hash/creation/'):
                            os.makedirs('./hash/creation/')
                            print(f"{Colors.BLUE}[Info]{Colors.RESET} Folder './hash/creation/' berhasil dibuat.")

                        with open(f'./hash/creation/{file_path}.txt', 'w') as f:
                            f.write(after_creation)
                            f.close()
                        
                        delete_files_in_vhd(mounting_path, 10)

                        subprocess.run(['sync'])

                        after_deletion = calculate_hash(vhd_file)

                        if not os.path.exists('./hash/deletion/'):
                            os.makedirs('./hash/deletion/')
                            print(f"{Colors.BLUE}[Info]{Colors.RESET} Folder './hash/deletion/' berhasil dibuat.")

                        with open(f'./hash/deletion/{file_path}.txt', 'w') as f:
                            f.write(after_deletion)
                            f.close()

                        print(f"\n{Colors.BLUE}[Info]{Colors.RESET} MD5 hash before file creation: {initial_hash}")
                        print(f"{Colors.BLUE}[Info]{Colors.RESET} MD5 hash after file creation: {after_creation}")
                        print(f"{Colors.BLUE}[Info]{Colors.RESET} MD5 hash after file deletion: {after_deletion}\n")
                        print(f"{Colors.BLUE}[Info]{Colors.RESET} menguji perbedaan hash\n")
                        calculate_diff(f'./hash/creation/{file_path}.txt', f'./hash/deletion/{file_path}.txt')

                    except Exception as e:
                        print(f"{Colors.RED}[Error]{Colors.RESET} : {e}")
                else:
                    print(f"{Colors.RED}[Error]{Colors.RESET} vhd tidak terpasang pada sistem.")
        elif operasi in ['-afs', '--analize-file-system']:
            if len(sys.argv) != 4:
                print(f"{Colors.RED}[Error]{Colors.RESET} Harap berikan path ke partisi dan nama file yang diinginkan. Usage: python3 script.py -afs <path> <file-name>")
                return
            
            partition_path = sys.argv[2]
            filename = sys.argv[3]
            AnalyzeFileSystem(partition_path, filename)
        else:
            print(f"{Colors.RED}[Error]{Colors.RESET} Operasi tidak dikenali. Coba '-h' untuk bantuan.")
    else:
        print(f"{Colors.RED}[Error]{Colors.RESET} Operasi tidak boleh kosong. Usage: python3 script.py <operation> <arguments>")

if __name__ == "__main__":
    main()
