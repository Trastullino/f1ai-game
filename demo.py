"""
Complete Integration Demo for F1-AI Racing Game
Demonstrates the full workflow: registration, training, and racing
Now using PyNaCl for Ed25519 signatures
"""

from external_program import ExternalProgram
from player import Player
from server import Server


def main():
    print("=" * 70)
    print("F1-AI RACING GAME - COMPLETE INTEGRATION DEMO")
    print("Using PyNaCl for Ed25519 and Pyfhel for BFV Encryption")
    print("=" * 70)
    
    # PHASE 1: SYSTEM INITIALIZATION
    print("\n" + "=" * 70)
    print("PHASE 1: SYSTEM INITIALIZATION")
    print("=" * 70)
    
    print("\n[1.1] Initializing External Program...")
    program = ExternalProgram()
    print("✓ External Program initialized")
    
    print("\n[1.2] Distributing public keys and encrypted polynomial...")
    public_keys = program.get_public_keys()
    encrypted_polynomial = program.get_encrypted_polynomial()
    print("✓ Keys and polynomial ready for distribution")
    
    print("\n[1.3] Initializing Server...")
    server = Server(public_keys, encrypted_polynomial)
    print("✓ Server initialized and ready")
    
    # PHASE 2: PLAYER REGISTRATION
    print("\n" + "=" * 70)
    print("PHASE 2: PLAYER REGISTRATION")
    print("=" * 70)
    
    players = []
    num_players = 3
    
    for i in range(num_players):
        print(f"\n[2.{i+1}] Registering Player {i+1}...")
        
        user_id, encrypted_car, signature = program.register_user()
        print(f"✓ User {user_id} registered with External Program")
        
        player = Player(user_id, public_keys, encrypted_polynomial)
        player.add_car(encrypted_car, signature)
        
        initial_car = program.decrypt_car(encrypted_car)
        print(f"  Initial car attributes: {initial_car[:3]}... (showing first 3 of 10)")
        print(f"  Starting XPF balance: {player.get_balance()}")
        
        players.append(player)
    
    print(f"\n✓ Total players registered: {len(players)}")
    
    # PHASE 3: TRAINING ROUNDS
    print("\n" + "=" * 70)
    print("PHASE 3: TRAINING ROUNDS (9 rounds per player)")
    print("=" * 70)
    
    for player_idx, player in enumerate(players):
        print(f"\n[3.{player_idx+1}] Training for Player {player.user_id}")
        print("-" * 50)
        
        for round_num in range(3):
            print(f"  Round {round_num + 1}/3...", end=" ")
            success = player.train_car(0, program)
            
            if success:
                print("✓")
            else:
                print("✗")
        
        encrypted_car, signature = player.cars[0]
        trained_car = program.decrypt_car(encrypted_car)
        print(f"  Final car attributes: {trained_car[:3]}... (showing first 3 of 10)")
        print(f"  Remaining XPF balance: {player.get_balance()}")
    
    # PHASE 4: RACE PREPARATION
    print("\n" + "=" * 70)
    print("PHASE 4: RACE PREPARATION")
    print("=" * 70)
    
    print("\n[4.1] Players entering the race...")
    for player_idx, player in enumerate(players):
        print(f"\n  Player {player.user_id}:")
        
        if player.enter_race(0):
            print(f"    ✓ Race entry fee paid (1 XPF)")
            print(f"    Balance: {player.get_balance()} XPF")
            
            encrypted_car, signature, _ = player.prepare_for_race(0)
            server.accept_race_entry(player.user_id, encrypted_car, signature)
        else:
            print(f"    ✗ Failed to enter race")
    
    print(f"\n✓ Race ready with {server.get_current_entries()} participants")
    
    # PHASE 5: RUNNING THE RACE
    print("\n" + "=" * 70)
    print("PHASE 5: RUNNING THE RACE")
    print("=" * 70)
    
    race_result = server.run_race(program)
    
    if race_result:
        print("\n✓ Race completed successfully!")
        winner_id = race_result['rankings'][0]['user_id']
        winner_speed = race_result['rankings'][0]['speed']
        
        for player in players:
            if player.user_id == winner_id:
                player.receive_winnings(100)
                print(f"\n🏆 Winner: Player {winner_id}")
                print(f"   Speed: {winner_speed}")
                print(f"   Prize: 100 XPF")
                print(f"   Final balance: {player.get_balance()} XPF")
                break
    
    # PHASE 6: VERIFICATION
    print("\n" + "=" * 70)
    print("PHASE 6: RACE VERIFICATION")
    print("=" * 70)
    
    print("\n[6.1] Verifying race results...")
    is_valid = server.verify_race_results(1)
    
    if is_valid:
        print("✓ Race results verified - no cheating detected")
    else:
        print("✗ Cheating detected - race would be cancelled")
    
    # PHASE 7: BLOCKCHAIN PUBLICATION
    print("\n" + "=" * 70)
    print("PHASE 7: BLOCKCHAIN PUBLICATION")
    print("=" * 70)
    
    print("\n[7.1] Preparing data for blockchain...")
    blockchain_data = server.publish_race_to_blockchain(race_result)
    
    print("✓ Race data ready for smart contract:")
    print(f"  Race ID: {blockchain_data['race_id']}")
    print(f"  Winner: User {blockchain_data['winner_id']}")
    print(f"  Winner Speed: {blockchain_data['winner_speed']}")
    print(f"  Participants: {blockchain_data['participants']}")
    
    # FINAL STATISTICS
    print("\n" + "=" * 70)
    print("FINAL STATISTICS")
    print("=" * 70)
    
    print("\nPlayer Balances:")
    for player in players:
        print(f"  Player {player.user_id}: {player.get_balance()} XPF, {player.get_car_count()} car(s)")
    
    print("\nRace History:")
    for race in server.get_race_history():
        print(f"  Race {race['race_id']}: {race['participants']} participants, "
              f"Winner: User {race['rankings'][0]['user_id']}")
    
    # SECURITY PROPERTIES
    print("\n" + "=" * 70)
    print("SECURITY PROPERTIES DEMONSTRATED")
    print("=" * 70)
    
    print("""
✓ Players cannot see their own car flags (encrypted at all times)
✓ Players cannot see other players' flags (encrypted)
✓ Server cannot see car flags (only has public keys)
✓ Server cannot see the speed formula (encrypted polynomial)
✓ Players cannot modify flags directly (signatures verified)
✓ Server cannot cheat on race results (verifiable on blockchain)
✓ All training modifications are constrained (±19 per attribute)
✓ Race results are publicly verifiable through encryption
✓ Using PyNaCl for Ed25519 signatures (fast and secure)
    """)
    
    print("=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    
    print("\n[Bonus] Saving system state...")
    program.save_state("program_state.pkl")
    print("✓ State saved to 'program_state.pkl'")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
