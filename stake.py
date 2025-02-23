import os
import random
import time
from web3 import Web3
from dotenv import load_dotenv
from eth_abi import encode
from banner import banner
from colorama import Fore

load_dotenv()
print(banner)

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise Exception("Private key not found in .env file")

RPC_URL = "https://testnet-rpc.monad.xyz/"
CHAIN_ID = 10143

web3 = Web3(Web3.HTTPProvider(RPC_URL))

if web3.is_connected():
    print(Fore.GREEN + "Berhasil terhubung ke Monad Testnet\n")
else:
    print(Fore.RED + "Connection failed.")
    exit(1)

print(Fore.GREEN + f"https://kintsu.xyz/\n")

account = web3.eth.account.from_key(PRIVATE_KEY)
wallet_address = account.address

contract_address = web3.to_checksum_address("0x07aabd925866e8353407e67c1d157836f7ad923e")

def stake(amount_in_ether):
    amount_in_wei = web3.to_wei(amount_in_ether, 'ether')
    nonce = web3.eth.get_transaction_count(wallet_address)
    gas_price = web3.eth.gas_price 

    stake_selector = web3.keccak(text="stake()")[:4].hex() 

    tx = {
        'chainId': CHAIN_ID,
        'gas': 10000000,
        'maxFeePerGas': gas_price,
        'maxPriorityFeePerGas': gas_price,
        'nonce': nonce,
        'to': contract_address,
        'value': amount_in_wei,
        'data': stake_selector 
    }

    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return web3.to_hex(tx_hash)

def unstake(amount_in_ether):
    amount_in_wei = web3.to_wei(amount_in_ether, 'ether')
    nonce = web3.eth.get_transaction_count(wallet_address)
    gas_price = web3.eth.gas_price 

    selector = "0x30af6b2e" 
    encoded_args = encode(['uint256'], [amount_in_wei])
    data = web3.to_bytes(hexstr=selector) + encoded_args

    tx = {
        'chainId': CHAIN_ID,
        'gas': 5000000,
        'maxFeePerGas': gas_price,
        'maxPriorityFeePerGas': gas_price,
        'nonce': nonce,
        'to': contract_address,
        'data': data
    }

    signed_tx = web3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return web3.to_hex(tx_hash)

def generate_random_amount(min_amount, max_amount):
    return round(random.uniform(min_amount, max_amount), 2)

if __name__ == "__main__":
    action_choice = input(Fore.CYAN + "Pilih opsi:\n1. Stake\n2. Stake & Unstake\nMasukkan pilihan (1/2): ")

    if action_choice == "1":
        loop_choice = input(Fore.CYAN + "\nPerlu looping?\n1. Ya\n2. Tidak\nMasukkan pilihan (1/2): ")

        if loop_choice == "1":
            iterations = int(input(Fore.CYAN + "Masukkan jumlah looping(5 kali): "))
            min_stake = float(input(Fore.CYAN + "Masukkan minimum Stake(0.1 MONAD): "))
            max_stake = float(input(Fore.CYAN + "Masukkan maksimal Stake(0.3 MONAD): "))
            for i in range(iterations):
                stake_amount = generate_random_amount(min_stake, max_stake)
                print(Fore.CYAN + f"✅ Stake {stake_amount} MONAD (Looping {i + 1}/{iterations})...")

                try:
                    stake_tx_hash = stake(stake_amount)
                    print(Fore.GREEN + f"✅ Hash: https://testnet.monadexplorer.com/tx/{stake_tx_hash}")
                except Exception as e:
                    print(Fore.RED + f"❌ Terjadi kesalahan saat melakukan stake: {e}")

                print(Fore.YELLOW + "🔄️ Menunggu 30 detik sebelum looping berikutnya...")
                time.sleep(30)
        else:
            stake_amount = float(input(Fore.CYAN + "Masukkan jumlah Stake(0.1 MONAD): "))
            print(Fore.CYAN +  f"✅ Stake {stake_amount} MONAD")

            try:
                stake_tx_hash = stake(stake_amount)
                print(Fore.GREEN + f"✅ Hash: https://testnet.monadexplorer.com/tx/{stake_tx_hash}")
            except Exception as e:
                print(Fore.RED + f"❌ Terjadi kesalahan saat melakukan stake: {e}")
    
    elif action_choice == "2":
        loop_choice = input(Fore.CYAN + "\nPerlu looping?\n1. Ya\n2. Tidak\nMasukkan pilihan (1/2): ")

        if loop_choice == "1":
            iterations = int(input(Fore.CYAN + "Masukkan jumlah looping(5 kali): "))
            min_stake = float(input(Fore.CYAN + "Masukkan jumlah minimum Stake(0.1 MONAD): "))
            max_stake = float(input(Fore.CYAN + "Masukkan jumlah maksimal Stake(0.3 MONAD): "))
            min_unstake = float(input(Fore.CYAN + "Masukkan jumlah minimum Unstake(0.01 MONAD): "))
            max_unstake = float(input(Fore.CYAN + "Masukkan jumlah maksimal Unstake(0.03 MONAD): "))
            for i in range(iterations):
                stake_amount = generate_random_amount(min_stake, max_stake)
                print(Fore.CYAN + f"✅ Stake {stake_amount} MONAD (Looping {i + 1}/{iterations})...")

                try:
                    stake_tx_hash = stake(stake_amount)
                    print(Fore.GREEN + f"✅ Hash: https://testnet.monadexplorer.com/tx/{stake_tx_hash}")
                except Exception as e:
                    print(Fore.RED + f"❌ Terjadi kesalahan saat melakukan stake: {e}")

                print(Fore.YELLOW + "⏳ Menunggu 10 detik untuk melakukan Unstake...")
                time.sleep(10)

                unstake_amount = generate_random_amount(min_unstake, max_unstake)
                print(Fore.CYAN + f"✅ Unstake {unstake_amount} MONAD (Looping {i + 1}/{iterations})...")

                try:
                    unstake_tx_hash = unstake(unstake_amount)
                    print(Fore.GREEN + f"✅ Hash: https://testnet.monadexplorer.com/tx/{unstake_tx_hash}")
                except Exception as e:
                    print(Fore.RED + f"❌ Terjadi kesalahan saat melakukan unstake: {e}")

                print(Fore.YELLOW + "🔄️ Menunggu 30 detik sebelum looping berikutnya...")
                time.sleep(30)
        else:
            stake_amount = float(input(Fore.CYAN + "Masukkan jumlah Stake(0.3 MONAD): "))
            unstake_amount = float(input(Fore.CYAN + "Masukkan jumlah Unstake(0.1 MONAD): "))
            print(Fore.CYAN + f"✅ Stake {stake_amount} MONAD")

            try:
                stake_tx_hash = stake(stake_amount)
                print(Fore.GREEN + f"✅ Hash transaksi Stake: https://testnet.monadexplorer.com/tx/{stake_tx_hash}")
            except Exception as e:
                print(Fore.RED + f"❌ Terjadi kesalahan saat melakukan stake: {e}")

            print(Fore.YELLOW + "⏳ Menunggu 10 detik untuk melakukan Unstake...")
            time.sleep(10)

            print(Fore.CYAN + f"✅ Unstake {unstake_amount} MONAD")

            try:
                unstake_tx_hash = unstake(unstake_amount)
                print(Fore.GREEN + f"✅ Hash: https://testnet.monadexplorer.com/tx/{unstake_tx_hash}")
            except Exception as e:
                print(Fore.RED + f"❌ Terjadi kesalahan saat melakukan unstake: {e}")

    else:
        print(Fore.RED + "[INFO] Pilihan tidak valid. Program berhenti.")