"""
Complete Integration Demo for F1-AI Racing Game
Now integrated with blockchain smart contract:
 - Players register cars ON-CHAIN using registerCar()
 - Server retrieves participants from blockchain
"""

from external_program import ExternalProgram
from player import Player
from server import Server

from blockchain_interface import BlockchainInterface
import json


def main():
    print("=" * 70)
    print("F1-AI RACING GAME - BLOCKCHAIN ENABLED")
    print("=" * 70)
    
    # PHASE 1: SYSTEM INITIALIZATION
    print("\n[1.1] Initializing External Program...")
    program = ExternalProgram()
    print("✓ External Program ready")
    
    print("\n[1.2] Distributing encrypted polynomial + public keys...")
    public_keys = program.get_public_keys()
    encrypted_polynomial = program.get_encrypted_polynomial()
    
    print("\n[1.3] Initializing Server...")
    server = Server(public_keys, encrypted_polynomial)
    print("✓ Server ready")

    print("\n[1.4] Connecting to Blockchain...")

    with open("deployment_ganache.json", "r") as f:
        deploy_info = json.load(f)

    rpc_url = "http://host.docker.internal:8545"
    contract_address = deploy_info["contract_address"]
    contract_abi = deploy_info["abi"]

   
    private_key = "0xa4b2e7d374c62957d5067828ae5f31802da8af884e8cac24a40f95be494a55a6"

    blockchain = BlockchainInterface(
        rpc_url,
        contract_address,
        contract_abi,
        private_key
    )

    # PHASE 2: PLAYER REGISTRATION
    print("\n" + "=" * 70)
    print("PHASE 2: PLAYER REGISTRATION")
    print("=" * 70)
    
    players = []
    num_players = 3
    
    for i in range(num_players):
        print(f"\nRegistering Player {i+1}...")
        
        user_id, encrypted_car, signature = program.register_user()
        
        player = Player(user_id, public_keys, encrypted_polynomial)
        player.add_car(encrypted_car, signature)
        
        decoded = program.decrypt_car(encrypted_car)
        print(f"  User {user_id} initial car: {decoded[:3]}... (3 of 10)")
        print(f"  XPF balance: {player.get_balance()}")
        
        players.append(player)
    
    # PHASE 3: TRAINING
    print("\n" + "=" * 70)
    print("PHASE 3: TRAINING")
    print("=" * 70)
    
    for player in players:
        print(f"\nTraining Player {player.user_id}:")
        for r in range(3):
            print(f"  Round {r+1}/3...", end=" ")
            if player.train_car(0, program):
                print("✓")
            else:
                print("✗")
    
    # ✅ PHASE 4: REGISTER CARS ON-CHAIN
    print("\n" + "=" * 70)
    print("PHASE 4: ON-CHAIN REGISTRATION")
    print("=" * 70)

    for player in players:
        print(f"\nPlayer {player.user_id}: entering race...")
        
        # deduct fee + sign updated car
        if not player.enter_race(0):
            print("  ✗ Failed: insufficient balance or other error")
            continue

        encrypted_car, signature, _ = player.prepare_for_race(0)

        receipt = blockchain.register_car(
            player.user_id,
            encrypted_car,
            signature
        )
        
        if receipt:
            print("  ✓ On-chain registration success")
        else:
            print("  ✗ Failed submitting to blockchain")
    
    # ✅ Retrieve on-chain entries and feed server
    print("\n[4.2] Fetching entries from blockchain...")
    chain_entries = blockchain.get_entries()

    for e in chain_entries:
        server.accept_race_entry(
            e['user_id'],
            e['encrypted_car'],
            e['signature']
        )

    print(f"✓ Total on-chain participants received: {server.get_current_entries()}")

    # PHASE 5: RUN THE RACE
    print("\n" + "=" * 70)
    print("PHASE 5: RUNNING RACE")
    print("=" * 70)
    
    race_result = server.run_race(program)
    
    if race_result:
        winner = race_result['rankings'][0]
        print(f"\n🏆 Winner is Player {winner['user_id']} (speed {winner['speed']})")
        
        # give reward locally
        for p in players:
            if p.user_id == winner['user_id']:
                p.receive_winnings(100)
                print(f"Prize paid. New balance: {p.get_balance()} XPF")

    print("\nDemo complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
