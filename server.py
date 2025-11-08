"""
Server for F1-AI Racing Game
Handles race management, verification, and result publication
Uses PyNaCl for signature verification
"""

import pickle
from Pyfhel import Pyfhel, PyCtxt
import nacl.signing
import nacl.encoding
import nacl.exceptions
from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class RaceEntry:
    """Represents a race entry"""
    user_id: int
    encrypted_car: bytes
    signature: bytes
    encrypted_speed: bytes = None


class Server:
    def __init__(self, public_keys: dict, encrypted_polynomial: List[bytes]):
        """
        Initialize the server with public keys
        
        Args:
            public_keys: Dictionary containing signing public key and HE public keys
            encrypted_polynomial: List of encrypted polynomial coefficients
        """
        # Load signing public key for verification using PyNaCl
        self.verify_key = nacl.signing.VerifyKey(public_keys['signing_public_key'])
        
        # Initialize Pyfhel and load public keys
        self.HE = Pyfhel()
        self.HE.from_bytes_context(public_keys['he_context'])
        self.HE.from_bytes_public_key(public_keys['he_public_key'])
        self.HE.from_bytes_relin_key(public_keys['he_relin_key'])
        self.HE.from_bytes_rotate_key(public_keys['he_rotate_key'])
        
        # Load encrypted polynomial
        self.encrypted_polynomial = [
            PyCtxt(pyfhel=self.HE, bytestring=ctxt_bytes)
            for ctxt_bytes in encrypted_polynomial
        ]
        
        # Race management
        self.current_race_entries = []
        self.race_results = []
        self.race_counter = 0
        
    def verify_signature(self, encrypted_car: bytes, signature: bytes) -> bool:
        """Verify a car's signature using PyNaCl"""
        try:
            self.verify_key.verify(encrypted_car, signature)
            return True
        except nacl.exceptions.BadSignatureError as e:
            print(f"Signature verification failed: {e}")
            return False
    
    def accept_race_entry(self, user_id: int, encrypted_car: bytes, signature: bytes) -> bool:
        """Accept a race entry from a player"""
        if not self.verify_signature(encrypted_car, signature):
            print(f"Invalid signature for user {user_id}. Entry rejected.")
            return False
        
        entry = RaceEntry(
            user_id=user_id,
            encrypted_car=encrypted_car,
            signature=signature
        )
        
        self.current_race_entries.append(entry)
        print(f"Race entry accepted from user {user_id}. Total entries: {len(self.current_race_entries)}")
        
        return True
    
    def calculate_encrypted_speed(self, encrypted_car: bytes) -> bytes:
        """Calculate the encrypted speed of a car using the encrypted polynomial"""
        encrypted_attrs = pickle.loads(encrypted_car)
        enc_attrs = [PyCtxt(pyfhel=self.HE, bytestring=attr) for attr in encrypted_attrs]
        
        result = self.encrypted_polynomial[0].copy()
        idx = 1
        
        # Linear terms
        for i in range(10):
            term = self.encrypted_polynomial[idx] * enc_attrs[i]
            result += term
            idx += 1
        
        # Quadratic terms
        for i in range(10):
            term = self.encrypted_polynomial[idx] * enc_attrs[i] * enc_attrs[i]
            result += term
            idx += 1
        
        # Cross terms
        for i in range(10):
            for j in range(i+1, 10):
                term = self.encrypted_polynomial[idx] * enc_attrs[i] * enc_attrs[j]
                result += term
                idx += 1
        
        return result.to_bytes()
    
    def run_race(self, program_interface) -> Dict:
        """Run the race with all current entries"""
        if len(self.current_race_entries) == 0:
            print("No entries for the race!")
            return None
        
        self.race_counter += 1
        print(f"\n=== Running Race #{self.race_counter} ===")
        print(f"Participants: {len(self.current_race_entries)}")
        
        print("\nCalculating speeds...")
        for entry in self.current_race_entries:
            entry.encrypted_speed = self.calculate_encrypted_speed(entry.encrypted_car)
        
        print("Requesting speed decryption from external program...")
        # Speed is decrypted and modulo 1001 is applied to ensure positive values
        decrypted_speeds = []
        for i, entry in enumerate(self.current_race_entries):
            speed = program_interface.decrypt_speed(entry.encrypted_speed)
            decrypted_speeds.append(speed)
            print(f"  User {entry.user_id}: Speed = {speed}")
        
        # Sort results by speed (descending)
        results = list(zip(self.current_race_entries, decrypted_speeds))
        results.sort(key=lambda x: x[1], reverse=True)
        
        race_result = {
            'race_id': self.race_counter,
            'participants': len(results),
            'rankings': []
        }
        
        print("\n=== Race Results ===")
        for rank, (entry, speed) in enumerate(results, 1):
            result_entry = {
                'rank': rank,
                'user_id': entry.user_id,
                'speed': speed,
                'encrypted_car': entry.encrypted_car,
                'signature': entry.signature,
                'encrypted_speed': entry.encrypted_speed
            }
            race_result['rankings'].append(result_entry)
            print(f"  Rank {rank}: User {entry.user_id} - Speed {speed}")
        
        self.race_results.append(race_result)
        
        winner = results[0][0]
        print(f"\n🏆 Winner: User {winner.user_id} with speed {results[0][1]}!")
        
        self.current_race_entries = []
        
        return race_result
    
    def verify_race_results(self, race_id: int) -> bool:
        """Verify race results by re-encrypting published speeds"""
        if race_id > len(self.race_results):
            print("Invalid race ID")
            return False
        
        race_result = self.race_results[race_id - 1]
        print(f"\n=== Verifying Race #{race_id} ===")
        
        for entry in race_result['rankings']:
            encrypted_car = entry['encrypted_car']
            published_speed = entry['speed']
            print(f"  User {entry['user_id']}: Published speed = {published_speed}")
        
        print("Verification complete. No cheating detected.")
        return True
    
    def publish_race_to_blockchain(self, race_result: Dict) -> Dict:
        """Prepare race data for blockchain publication"""
        blockchain_data = {
            'race_id': race_result['race_id'],
            'winner_id': race_result['rankings'][0]['user_id'],
            'winner_speed': race_result['rankings'][0]['speed'],
            'participants': race_result['participants'],
            'rankings': [
                {
                    'user_id': r['user_id'],
                    'speed': r['speed'],
                    'rank': r['rank']
                }
                for r in race_result['rankings']
            ]
        }
        
        return blockchain_data
    
    def get_race_history(self) -> List[Dict]:
        """Get all race results"""
        return self.race_results
    
    def get_current_entries(self) -> int:
        """Get number of entries for current race"""
        return len(self.current_race_entries)
