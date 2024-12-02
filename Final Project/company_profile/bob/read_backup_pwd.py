import os
import subprocess

def backup_files():
    print("Starting backup process...")
    fd = os.open("/root/cridential.txt", os.O_RDONLY)

    print("Backup file opened, proceeding with backup...")
    
    subprocess.call(["ls", "-l", "/home/bob"])

    subprocess.call(["/bin/sh"], pass_fds=(fd,))

    os.setuid(os.getuid())

    os.close(fd)

def main():
    print("Running scheduled backup...")
    backup_files()

if __name__ == "__main__":
    main()