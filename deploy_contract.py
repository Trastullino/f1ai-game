"""
Deploy F1AIRacing Smart Contract
Supports multiple networks: local (Ganache), testnets (Sepolia, Mumbai), mainnet
"""

from web3 import Web3
from eth_account import Account
from solcx import compile_standard, install_solc
import json
import sys
import os


def compile_contract():
    """Compile the Solidity contract"""
    print("Installing Solidity compiler...")
    install_solc('0.8.20')
    
    print("Reading contract source...")
    with open('F1AIRacing.sol', 'r') as f:
        contract_source = f.read()
    
    print("Compiling contract...")
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"F1AIRacing.sol": {"content": contract_source}},
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                    }
                },
                "optimizer": {
                    "enabled": True,
                    "runs": 200
                }
            },
        },
        solc_version="0.8.20",
    )
    
    # Extract contract data
    contract_data = compiled_sol['contracts']['F1AIRacing.sol']['F1AIRacing']
    bytecode = contract_data['evm']['bytecode']['object']
    abi = contract_data['abi']
    
    print("✓ Contract compiled successfully")
    return bytecode, abi


def save_deployment_info(contract_address, abi, network):
    """Save deployment information for later use"""
    deployment_info = {
        'contract_address': contract_address,
        'abi': abi,
        'network': network
    }
    
    with open(f'deployment_{network}.json', 'w') as f:
        json.dump(deployment_info, f, indent=2)
    
    print(f"✓ Deployment info saved to deployment_{network}.json")


def deploy_contract(rpc_url, private_key, server_address, network_name="local"):
    """Deploy contract to specified network"""
    
    print(f"\n{'='*70}")
    print(f"DEPLOYING F1AI RACING CONTRACT TO {network_name.upper()}")
    print(f"{'='*70}\n")
    
    # Compile contract
    bytecode, abi = compile_contract()
    
    # Connect to network
    print(f"Connecting to {network_name} at {rpc_url}...")
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    if not w3.is_connected():
        print("✗ Failed to connect to network")
        return None, None
    
    print(f"✓ Connected to network (Chain ID: {w3.eth.chain_id})")
    
    # Setup account
    account = Account.from_key(private_key)
    print(f"✓ Using deployer address: {account.address}")
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    balance_eth = w3.from_wei(balance, 'ether')
    print(f"✓ Account balance: {balance_eth} ETH")
    
    if balance == 0:
        print("✗ Account has no funds!")
        return None, None
    
    # Create contract instance
    print("\nPreparing deployment transaction...")
    F1AIRacing = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Estimate gas
    try:
        gas_estimate = F1AIRacing.constructor(server_address).estimate_gas({
            'from': account.address
        })
        print(f"✓ Estimated gas: {gas_estimate}")
    except Exception as e:
        print(f"⚠ Could not estimate gas: {e}")
        gas_estimate = 3000000  # Fallback
    
    # Build transaction
    nonce = w3.eth.get_transaction_count(account.address)
    
    # Get gas price
    try:
        gas_price = w3.eth.gas_price
    except:
        gas_price = w3.to_wei('50', 'gwei')  # Fallback
    
    print(f"✓ Gas price: {w3.from_wei(gas_price, 'gwei')} gwei")
    
    transaction = F1AIRacing.constructor(server_address).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': gas_estimate + 100000,  # Add buffer
        'gasPrice': gas_price
    })
    
    # Sign transaction
    print("\nSigning transaction...")
    signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
    
    # Send transaction
    print("Sending transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"✓ Transaction sent: {tx_hash.hex()}")
    
    # Wait for receipt
    print("Waiting for confirmation...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
    
    if tx_receipt['status'] == 1:
        contract_address = tx_receipt['contractAddress']
        print(f"\n{'='*70}")
        print("✓ CONTRACT DEPLOYED SUCCESSFULLY!")
        print(f"{'='*70}")
        print(f"\nContract Address: {contract_address}")
        print(f"Transaction Hash: {tx_hash.hex()}")
        print(f"Block Number: {tx_receipt['blockNumber']}")
        print(f"Gas Used: {tx_receipt['gasUsed']}")
        print(f"Server Address: {server_address}")
        
        # Save deployment info
        save_deployment_info(contract_address, abi, network_name)
        
        return contract_address, abi
    else:
        print("✗ Deployment failed!")
        return None, None


def deploy_local_ganache():
    """Deploy to local Ganache"""
    print("\n📍 Deploying to LOCAL GANACHE")
    print("Make sure Ganache is running on http://127.0.0.1:8545")
    
    rpc_url = "http://127.0.0.1:8545"
    
    # Default Ganache account
    private_key = "0x4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d"
    server_address = "0x90F8bf6A479f320ead074411a4B0e7944Ea8c9C1"  # First Ganache account
    
    return deploy_contract(rpc_url, private_key, server_address, "ganache")


def deploy_sepolia(private_key, server_address, infura_key):
    """Deploy to Sepolia testnet"""
    print("\n📍 Deploying to SEPOLIA TESTNET")
    
    rpc_url = f"https://sepolia.infura.io/v3/{infura_key}"
    
    return deploy_contract(rpc_url, private_key, server_address, "sepolia")


def deploy_mumbai(private_key, server_address, infura_key):
    """Deploy to Mumbai testnet (Polygon)"""
    print("\n📍 Deploying to MUMBAI TESTNET (Polygon)")
    
    rpc_url = f"https://polygon-mumbai.infura.io/v3/{infura_key}"
    
    return deploy_contract(rpc_url, private_key, server_address, "mumbai")


def interactive_deploy():
    """Interactive deployment"""
    print("\n" + "="*70)
    print("F1-AI RACING CONTRACT DEPLOYMENT")
    print("="*70)
    
    print("\nSelect network:")
    print("1. Local Ganache (default)")
    print("2. Sepolia Testnet")
    print("3. Mumbai Testnet (Polygon)")
    print("4. Custom RPC")
    
    choice = input("\nEnter choice (1-4, default=1): ").strip() or "1"
    
    if choice == "1":
        return deploy_local_ganache()
    
    elif choice == "2":
        print("\nSepolia Deployment")
        private_key = input("Enter private key (with 0x prefix): ").strip()
        server_address = input("Enter server address: ").strip()
        infura_key = input("Enter Infura API key: ").strip()
        return deploy_sepolia(private_key, server_address, infura_key)
    
    elif choice == "3":
        print("\nMumbai Deployment")
        private_key = input("Enter private key (with 0x prefix): ").strip()
        server_address = input("Enter server address: ").strip()
        infura_key = input("Enter Infura API key: ").strip()
        return deploy_mumbai(private_key, server_address, infura_key)
    
    elif choice == "4":
        print("\nCustom RPC Deployment")
        rpc_url = input("Enter RPC URL: ").strip()
        private_key = input("Enter private key (with 0x prefix): ").strip()
        server_address = input("Enter server address: ").strip()
        network_name = input("Enter network name: ").strip()
        return deploy_contract(rpc_url, private_key, server_address, network_name)
    
    else:
        print("Invalid choice!")
        return None, None


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              F1-AI RACING SMART CONTRACT DEPLOYER                    ║
║                                                                      ║
║  This script will deploy the F1AIRacing.sol contract to your        ║
║  chosen blockchain network.                                          ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Check if contract file exists
    if not os.path.exists('F1AIRacing.sol'):
        print("✗ F1AIRacing.sol not found in current directory!")
        sys.exit(1)
    
    try:
        contract_address, abi = interactive_deploy()
        
        if contract_address:
            print("\n" + "="*70)
            print("DEPLOYMENT COMPLETE!")
            print("="*70)
            print(f"\n✓ Contract Address: {contract_address}")
            print(f"✓ ABI and deployment info saved")
            print(f"\nNext steps:")
            print(f"1. Update demo.py with contract address")
            print(f"2. Update blockchain_interface.py configuration")
            print(f"3. Run demo: python demo.py")
            
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled by user")
    except Exception as e:
        print(f"\n✗ Error during deployment: {e}")
        import traceback
        traceback.print_exc()
