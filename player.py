"""
Player Client for F1-AI Racing Game
Handles player interactions, car management, and race participation
Uses PyNaCl for signature verification
"""

import pickle
from Pyfhel import Pyfhel, PyCtxt
import nacl.signing
import nacl.encoding
import nacl.exceptions
from typing import List, Tuple


class Player:
    def __init__(self, user_id: int, public_keys: dict, encrypted_polynomial: List[bytes]):
        """
        Initialize a player with public keys and encrypted polynomial
        
        Args:
            user_id: Player's unique identifier
            public_keys: Dictionary containing signing public key and HE public keys
            encrypted_polynomial: List of encrypted polynomial coefficients
        """
        self.user_id = user_id
        self.xpf_balance = 10  # Starting balance
        
        # Load signing public key using PyNaCl
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
        
        # Store player's cars
        self.cars = []  # List of (encrypted_car, signature) tuples
        self.car_speeds = []  # List of encrypted speeds
        
    def add_car(self, encrypted_car: bytes, signature: bytes):
        """Add a car to the player's collection"""
        if self.verify_signature(encrypted_car, signature):
            self.cars.append((encrypted_car, signature))
            print(f"Car added to collection. Total cars: {len(self.cars)}")
        else:
            print("Invalid signature! Car not added.")
    
    def verify_signature(self, encrypted_car: bytes, signature: bytes) -> bool:
        """Verify a car's signature using PyNaCl"""
        try:
            self.verify_key.verify(encrypted_car, signature)
            return True
        except nacl.exceptions.BadSignatureError:
            return False
    
    def calculate_car_speed(self, car_index: int) -> bytes:
        """
        Calculate the encrypted speed of one of the player's cars
        Returns encrypted speed
        """
        if car_index >= len(self.cars):
            print("Invalid car index")
            return None
        
        encrypted_car, _ = self.cars[car_index]
        encrypted_attrs = pickle.loads(encrypted_car)
        enc_attrs = [PyCtxt(pyfhel=self.HE, bytestring=attr) for attr in encrypted_attrs]
        
        # Calculate speed using encrypted polynomial
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
        
        encrypted_speed = result.to_bytes()
        
        if car_index >= len(self.car_speeds):
            self.car_speeds.extend([None] * (car_index - len(self.car_speeds) + 1))
        self.car_speeds[car_index] = encrypted_speed
        
        return encrypted_speed
    
    def train_car(self, car_index: int, program_interface) -> bool:
        """
        Train a car by sending it to the external program
        Costs 1 XPF token
        """
        if self.xpf_balance < 1:
            print("Insufficient XPF tokens!")
            return False
        
        if car_index >= len(self.cars):
            print("Invalid car index")
            return False
        
        self.xpf_balance -= 1
        print(f"Paid 1 XPF. Remaining balance: {self.xpf_balance}")
        
        encrypted_car, signature = self.cars[car_index]
        new_car, new_sig, success = program_interface.train_car(
            self.user_id, car_index, encrypted_car, signature
        )
        
        if success:
            self.cars[car_index] = (new_car, new_sig)
            print("Training successful! Car updated.")
            
            enc_speed = self.calculate_car_speed(car_index)
            decrypted_speed = program_interface.decrypt_speed(enc_speed)
            print(f"New car speed: {decrypted_speed}")
            
            return True
        else:
            self.xpf_balance += 1
            print("Training failed. Token refunded.")
            return False
    
    def prepare_for_race(self, car_index: int) -> Tuple[bytes, bytes, bytes]:
        """
        Prepare a car for racing
        Returns: (encrypted_car, signature, encrypted_speed)
        """
        if car_index >= len(self.cars):
            print("Invalid car index")
            return None, None, None
        
        encrypted_car, signature = self.cars[car_index]
        
        if car_index >= len(self.car_speeds) or self.car_speeds[car_index] is None:
            encrypted_speed = self.calculate_car_speed(car_index)
        else:
            encrypted_speed = self.car_speeds[car_index]
        
        return encrypted_car, signature, encrypted_speed
    
    def enter_race(self, car_index: int) -> bool:
        """Enter a race with the specified car (costs 1 XPF)"""
        if self.xpf_balance < 1:
            print("Insufficient XPF tokens!")
            return False
        
        self.xpf_balance -= 1
        print(f"Paid 1 XPF to enter race. Remaining balance: {self.xpf_balance}")
        
        encrypted_car, signature, encrypted_speed = self.prepare_for_race(car_index)
        
        if encrypted_car is None:
            self.xpf_balance += 1
            return False
        
        return True
    
    def receive_winnings(self, amount: int):
        """Receive prize money from winning a race"""
        self.xpf_balance += amount
        print(f"Received {amount} XPF! New balance: {self.xpf_balance}")
    
    def get_car_count(self) -> int:
        """Get number of cars owned"""
        return len(self.cars)
    
    def get_balance(self) -> int:
        """Get current XPF balance"""
        return self.xpf_balance
