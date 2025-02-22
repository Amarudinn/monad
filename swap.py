import os
import time
from web3 import Web3
from dotenv import load_dotenv
from banner import banner
from colorama import Fore

load_dotenv()
print(banner)

PRIVATE_KEY = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEY:
    raise ValueError("Private key not found in .env file")

RPC_URL = "https://testnet-rpc.monad.xyz"
CHAIN_ID = 10143

web3 = Web3(Web3.HTTPProvider(RPC_URL))

if web3.is_connected():
    print(Fore.GREEN + "Berhasil terhubung ke Monad Testnet\n")
else:
    print(Fore.RED + "Connection failed.")
    exit(1)

UNISWAP_V2_ROUTER_ADDRESS = "0xCa810D095e90Daae6e867c19DF6D9A8C56db2c89"
TOKEN_ADDRESSES = {
    "YAKI": "0xfe140e1dCe99Be9F4F15d657CD9b7BF622270C50",
    "USDC": "0xf817257fed379853cDe0fa4F97AB987181B1E5Ea",
    "CHOG": "0xE0590015A873bF326bd645c3E1266d4db41C4E6B",
    "AIT": "0x97c37Fa4cC27c468Fcf19509f4e2bf2fd6C48C15"
}

web3 = Web3(Web3.HTTPProvider(RPC_URL))
if not web3.is_connected():
    raise ConnectionError("Failed to connect to RPC URL")

uniswap_v2_router_abi = '''
[
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactETHForTokens",
        "outputs": [
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForETH",
        "outputs": [
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
'''

erc20_abi = '''
[
    {
        "constant": true,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    }
]
'''

uniswap_router = web3.eth.contract(address=Web3.to_checksum_address(UNISWAP_V2_ROUTER_ADDRESS), abi=uniswap_v2_router_abi)

def get_token_decimals(token_address):
    token_contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=erc20_abi)
    return token_contract.functions.decimals().call()

def format_token_amount(amount, decimals):
    return amount / (10 ** decimals)

def swap_eth_for_tokens(account, private_key, amount_in_wei, amount_out_min, deadline, token_address):
    path = [web3.to_checksum_address("0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701"),
            web3.to_checksum_address(token_address)]

    gas_price = web3.eth.gas_price

    try:
        nonce = web3.eth.get_transaction_count(account.address, "pending")

        transaction = uniswap_router.functions.swapExactETHForTokens(
            amount_out_min,
            path,
            account.address,
            deadline
        ).build_transaction({
            'from': account.address,
            'value': amount_in_wei,
            'gas': 200000,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': CHAIN_ID
        })

        signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(Fore.CYAN + f"✅ Hash: {web3.to_hex(tx_hash)}")
        return web3.to_hex(tx_hash)

    except Exception as e:
        print(f"An error occurred: {e}")
        raise

def swap_tokens_for_eth(account, private_key, token_amount, amount_out_min, deadline, token_address, token_name):
    path = [web3.to_checksum_address(token_address),
            web3.to_checksum_address("0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701")]

    gas_price = web3.eth.gas_price
    gas_limit = 200000 

    try:
        nonce = web3.eth.get_transaction_count(account.address, "pending")

        token_contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=erc20_abi)
        approve_txn = token_contract.functions.approve(
            Web3.to_checksum_address(UNISWAP_V2_ROUTER_ADDRESS),
            token_amount
        ).build_transaction({
            'from': account.address,
            'gas': 100000,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': CHAIN_ID
        })

        signed_approve_txn = web3.eth.account.sign_transaction(approve_txn, private_key=private_key)
        web3.eth.send_raw_transaction(signed_approve_txn.raw_transaction)
        nonce += 1 

        transaction = uniswap_router.functions.swapExactTokensForETH(
            token_amount,
            amount_out_min,
            path,
            account.address,
            deadline
        ).build_transaction({
            'from': account.address,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': CHAIN_ID
        })

        signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

        tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        token_decimals = get_token_decimals(token_address)
        formatted_amount = format_token_amount(token_amount, token_decimals)
        print(Fore.CYAN + f"✅ Unswap berhasil {formatted_amount} {token_name} > MONAD")
        return web3.to_hex(tx_hash)

    except Exception as e:
        print(f"An error occurred during unswap: {e}")
        raise

def input_eth_amount():
    try:
        eth_amount = float(input(Fore.CYAN + "Masukan jumlah untuk swap (0.1): "))
        if eth_amount <= 0:
            raise ValueError("Jumlah Monad harus lebih besar dari 0.000001")
    except ValueError as e:
        print(f"Error: {e}")
        exit()

    return eth_amount

def input_looping_choice():
    while True:
        looping_choice = input(Fore.CYAN + "\nPerlu looping?\n1. Ya\n2. Tidak\nMasukan pilihan (1/2): ")
        if looping_choice == "1":
            loop_duration = int(input(Fore.CYAN + "Berapa lama untuk looping(detik): "))
            return True, loop_duration
        elif looping_choice == "2":
            return False, 0
        else:
            print(Fore.RED + "[INFO] Pilihan tidak valid, masukan pilihan 1-2")

def get_account_balance(account):
    balance = web3.eth.get_balance(account.address)
    return balance

def get_token_balance(account, token_address):
    token_contract = web3.eth.contract(address=Web3.to_checksum_address(token_address), abi=erc20_abi)
    return token_contract.functions.balanceOf(account.address).call()

if __name__ == "__main__":
    while True:
        print(Fore.CYAN + "Masukan token yang ingin di swap:")
        print(Fore.CYAN + "1. YAKI")
        print(Fore.CYAN + "2. USDC")
        print(Fore.CYAN + "3. CHOG")
        print(Fore.CYAN + "4. AIT")
        token_choice = input(Fore.CYAN + "Masukan pilihan (1-4): ")

        if token_choice == "1":
            token_name = "YAKI"
            token_address = TOKEN_ADDRESSES["YAKI"]
            break 
        elif token_choice == "2":
            token_name = "USDC"
            token_address = TOKEN_ADDRESSES["USDC"]
            break 
        elif token_choice == "3":
            token_name = "CHOG"
            token_address = TOKEN_ADDRESSES["CHOG"]
            break 
        elif token_choice == "4":
            token_name = "AIT"
            token_address = TOKEN_ADDRESSES["AIT"]
            break
        else:
            print(Fore.RED + "[INFO] Pilihan tidak valid. Silakan pilih 1-4.\n")

    eth_amount = input_eth_amount()

    should_loop, loop_duration = input_looping_choice()

    account = web3.eth.account.from_key(PRIVATE_KEY)

    amount_in_wei = web3.to_wei(eth_amount, 'ether')

    if get_account_balance(account) < amount_in_wei:
        print(Fore.RED + f"❌ Saldo monad tidak cukup untuk swap")
        exit()

    while True:
        tx_hash = swap_eth_for_tokens(account, PRIVATE_KEY, amount_in_wei, 0, int(web3.eth.get_block('latest').timestamp) + 300, token_address)
        print(Fore.CYAN + f"✅ Swap berhasil {eth_amount} MONAD > {token_name}")

        time.sleep(5)

        token_balance = get_token_balance(account, token_address)
        if token_balance > 0:
            unswap_amount = int(token_balance * 0.9)  # 90% Unswap
            if unswap_amount > 0:
                unswap_tx_hash = swap_tokens_for_eth(account, PRIVATE_KEY, unswap_amount, 0, int(web3.eth.get_block('latest').timestamp) + 300, token_address, token_name)

        if should_loop:
            print(Fore.YELLOW + f"🔄️ Menunggu {loop_duration} detik untuk transaksi berikutnya...")
            time.sleep(loop_duration)
        else:
            break