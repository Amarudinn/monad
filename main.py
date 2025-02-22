import os
from colorama import Fore
from banner import banner

print(banner)

def main():
    while True:
        print(Fore.CYAN + "\nPilih opsi:")
        print(Fore.CYAN + "1. Multisender")
        print(Fore.CYAN + "2. Swap & Unswap")
        print(Fore.CYAN + "0. Keluar\n")
        
        pilihan = input(Fore.CYAN + "Masukkan opsi (1-2): ")
        
        if pilihan == "1":
            os.system("python multisend.py")
        elif pilihan == "2":
            os.system("python swap.py")
        elif pilihan == "0":
            print(Fore.RED + "Keluar dari program.")
            break
        else:
            print(Fore.RED + "[INFO] Pilihan tidak valid, silakan pilih 1-2")

if __name__ == "__main__":
    main()
