import os
import time
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from colorama import Fore
from banner import banner

load_dotenv()
print(banner)

PRIVATE_KEYS = os.getenv("PRIVATE_KEY")
if not PRIVATE_KEYS:
    raise ValueError(Fore.RED + "Private key not found in .env file")

PRIVATE_KEYS = PRIVATE_KEYS.split(",")

RPC_URL = "https://testnet-rpc.monad.xyz/"
CHAIN_ID = 10143

web3 = Web3(Web3.HTTPProvider(RPC_URL))

if web3.is_connected():
    print(Fore.GREEN + "Berhasil terhubung ke Monad Testnet\n")
else:
    print(Fore.RED + "Connection failed.")
    exit(1)

CONTRACT_ADDRESS = "0x8129De2f887bE9fC0036Ce913C60361Cc2DC1F1f"
ABI = [
	{
		"inputs": [],
		"name": "claimTokens",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_tokenAddress",
				"type": "address"
			}
		],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "sender",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "FeeReceived",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "previousOwner",
				"type": "address"
			},
			{
				"indexed": True,
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_fee",
				"type": "uint256"
			}
		],
		"name": "setClaimFee",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_amount",
				"type": "uint256"
			}
		],
		"name": "setTokenAmount",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": True,
				"internalType": "address",
				"name": "receiver",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "amount",
				"type": "uint256"
			}
		],
		"name": "TokensClaimed",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "newTotalToken",
				"type": "uint256"
			}
		],
		"name": "TotalTokenUpdated",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "withdrawFees",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "withdrawTokens",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"stateMutability": "payable",
		"type": "receive"
	},
	{
		"inputs": [],
		"name": "claimFee",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getTokenBalance",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "hasClaimed",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "tokenAddress",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "tokenAmount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "totalToken",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

contract = web3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)

CLAIM_FEE = web3.to_wei(0.1, 'ether')

def claim_tokens(private_key):
    gas_price = web3.eth.gas_price
    while True:
        try:
            account = Account.from_key(private_key)

            transaction = contract.functions.claimTokens().build_transaction({
                'from': account.address,
                'value': CLAIM_FEE,
                'gas': 200000, 
                'gasPrice': gas_price,
                'nonce': web3.eth.get_transaction_count(account.address),
                'chainId': CHAIN_ID
            })

            signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)

            tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            print(Fore.CYAN + f"✅ Transaksi terkirim")

            receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

            if receipt.status == 1:
                print(Fore.CYAN + f"✅ Transaksi berhasil!")
                break
            else:
                print(Fore.RED + f"❌ Transaksi gagal!")
                break 

        except Exception as e:
            error_message = str(e)

            if 'replacement transaction underpriced' in error_message or 'nonce too low' in error_message:
                gas_price += web3.to_wei(2, 'gwei') 
                print(Fore.YELLOW + f"🔄️ Gas fee terlalu rendah mencoba menaikan gas fee")
            elif 'out of gas' in error_message:
                gas_price += web3.to_wei(5, 'gwei')
                print(Fore.YELLOW + f"🔄️ Gas fee terlalu rendah mencoba menaikan gas fee")
            else:
                print(Fore.RED + f"Non-gas-related error for account: {error_message}")
                return

if __name__ == "__main__":
    while True:
        for private_key in PRIVATE_KEYS:
            claim_tokens(private_key)
        print(Fore.YELLOW + "⏳ Menunggu 10 detik untuk transaksi berikutnya...")
        time.sleep(10)
