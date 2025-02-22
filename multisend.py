import os
from web3 import Web3
from dotenv import load_dotenv
from time import sleep
from colorama import Fore
from banner import banner

load_dotenv()
print(banner)

private_key = os.getenv("PRIVATE_KEY")
RPC_URL = "https://testnet-rpc.monad.xyz"
CHAIN_ID = 10143

web3 = Web3(Web3.HTTPProvider(RPC_URL))

if web3.is_connected():
    print(Fore.GREEN + "Berhasil terhubung ke Monad Testnet")
else:
    print(Fore.RED + "Connection failed.")
    exit(1)

account = web3.eth.account.from_key(private_key)
sender_address = account.address

def send_eth(to_address, amount):
    nonce = web3.eth.get_transaction_count(sender_address)
    gas_price = web3.eth.gas_price
    gas_limit = 21000  

    while True:
        try:
            txn = {
                'to': to_address,
                'value': amount,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': CHAIN_ID
            }

            signed_txn = web3.eth.account.sign_transaction(txn, private_key)
            txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            print(Fore.CYAN + f"✅ Transaksi terkirim! Hash: {web3.to_hex(txn_hash)}")

            receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
            print(Fore.CYAN + f"✅ Transaksi berhasil!")
            break

        except Exception as e:
            if "replacement transaction underpriced" in str(e):
                gas_price = int(gas_price * 1.1)
                print(Fore.YELLOW + f"🔄️ Gas price terlalu rendah, mencoba dengan gas price baru: {gas_price}")
            elif "nonce too low" in str(e):
                nonce = web3.eth.get_transaction_count(sender_address)
                print(Fore.YELLOW + f"🔄️ Nonce terlalu rendah, mengambil nonce baru: {nonce}")
            else:
                print(Fore.RED + f"[INFO] Gagal mengirim ke {to_address}: {e}")
                break

with open('address.txt', 'r') as file:
    addresses = file.readlines()

print(Fore.GREEN + f"\nTotal address: {len(addresses)}")

amount_to_send = 0

print(Fore.CYAN + "\nMenggunakan jeda antar address?")
print(Fore.CYAN + "1. Ya")
print(Fore.CYAN + "2. Tidak")
choice_jeda = input(Fore.CYAN + "Masukan pilihan (1/2) : ")

if choice_jeda == '1':
    jeda = int(input(Fore.CYAN + "Berapa jeda antar address(detik): "))
else:
    jeda = 0

print(Fore.CYAN + "\nPerlu looping atau tidak?")
print(Fore.CYAN + "1. Ya")
print(Fore.CYAN + "2. Tidak")
choice_loop = input(Fore.CYAN + "Masukan pilihan (1/2) : ")

if choice_loop == '1':
    loop_delay = int(input(Fore.CYAN + "Berapa lama jeda looping(dalam detik): "))
    loop_flag = True 
else:
    loop_flag = False  

amount_to_send = float(input(Fore.CYAN + "Berapa jumlah yang akan dikirim (misal: 0.01 NEX): "))

amount_to_send_wei = int(amount_to_send * 10**18)  

if loop_flag:
    while True:
        for address in addresses:
            address = address.strip()
            if web3.is_address(address):
                try:
                    send_eth(address, amount_to_send_wei)
                except Exception as e:
                    print(Fore.RED + f"[INFO] Gagal mengirim ke {address}: {e}")
            else:
                print(Fore.RED + f"[INFO] Alamat tidak valid: {address}")

            if jeda > 0:
                print(Fore.YELLOW + f"🔄️ Menunggu {jeda} detik sebelum melanjutkan transaksi berikutnya...")
                sleep(jeda)

        if loop_delay > 0:
            print(Fore.YELLOW + f"🔄️ Menunggu {loop_delay} detik sebelum melanjutkan loop...")
            sleep(loop_delay)

else:
    for address in addresses:
        address = address.strip()
        if web3.is_address(address):
            try:
                send_eth(address, amount_to_send_wei)
            except Exception as e:
                print(Fore.RED + f"[INFO] Gagal mengirim ke {address}: {e}")
        else:
            print(Fore.RED + f"[INFO] Alamat tidak valid: {address}")

        if jeda > 0:
            print(Fore.YELLOW + f"🔄️ Menunggu {jeda} detik sebelum melanjutkan transaksi berikutnya...")
            sleep(jeda)
