"""
Blockchain Integration for F1-AI Racing Game
Handles Web3 interactions with the smart contract
"""

from web3 import Web3
from eth_account import Account
import json


class BlockchainInterface:
    def __init__(self, rpc_url: str, contract_address: str, contract_abi: list, private_key: str):
        """
        Initialize blockchain interface
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.contract_address = Web3.to_checksum_address(contract_address)
        self.contract = self.w3.eth.contract(address=self.contract_address, abi=contract_abi)
        
        # Set up account
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        
        if not self.w3.is_connected():
            raise Exception("Failed to connect to blockchain")
        
        print(f"Connected to blockchain at {rpc_url}")
        print(f"Using account: {self.address}")
    
    def register_car(self, user_id: int, encrypted_car: bytes, signature: bytes):
        """Submit car registration on-chain"""
        try:
            gas_estimate = self.contract.functions.registerCar(
                user_id,
                encrypted_car,
                signature
            ).estimate_gas({'from': self.address})

            txn = self.contract.functions.registerCar(
                user_id,
                encrypted_car,
                signature
            ).build_transaction({
                'from': self.address,
                'nonce': self.w3.eth.get_transaction_count(self.address),
                'gas': gas_estimate + 50000,
                'maxFeePerGas': self.w3.to_wei(100, 'gwei'),
                'maxPriorityFeePerGas': self.w3.to_wei(2, 'gwei')
            })

            signed = self.account.sign_transaction(txn)
            tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            print(f"Car registered on chain for user {user_id}. Tx: {tx_hash.hex()}")
            return receipt

        except Exception as e:
            print(f"Error registering car: {e}")
        return None

    
    def get_entries(self) -> list:
        """Get all entries from chain"""
        try:
            entries = self.contract.functions.getAllEntries().call()
            parsed_entries = []
            for entry in entries:
                parsed_entries.append({
                    'player_address': entry[0],
                    'user_id': entry[1],
                    'encrypted_car': entry[2],
                    'signature': entry[3],
                    'timestamp': entry[4]
                })
            return parsed_entries

        except Exception as e:
            print(f"Error reading entries: {e}")
            return []


if __name__ == "__main__":
    print("Blockchain Interface ready.")
