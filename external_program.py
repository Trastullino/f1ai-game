"""
External Program for F1-AI Racing Game
Handles key generation, car creation, training, and decryption
Uses Ed25519 (via PyNaCl) for signatures and BFV homomorphic encryption
"""

import numpy as np
from Pyfhel import Pyfhel, PyCtxt
import nacl.signing
import nacl.encoding
import nacl.exceptions
import pickle
import json
from typing import Tuple, List
import secrets


class ExternalProgram:
    def __init__(self):
        """Initialize the external program with key generation"""
        print("Generating Ed25519 keys with PyNaCl...")
        # Generate Ed25519 signing keys using PyNaCl
        self.signing_key = nacl.signing.SigningKey.generate()
        self.verify_key = self.signing_key.verify_key
        
        print("Initializing BFV homomorphic encryption...")
        # Initialize Pyfhel for BFV homomorphic encryption
        self.HE = Pyfhel()
        self.HE.contextGen(scheme='bfv', n=8192, t_bits=20, t=65537)
        self.HE.keyGen()
        self.HE.relinKeyGen()
        self.HE.rotateKeyGen()
        
        print("Generating speed polynomial...")
        # Generate speed polynomial coefficients (66 coefficients for degree 2 polynomial with 10 variables)
        self.speed_polynomial_coeffs = self._generate_speed_polynomial()
        
        print("Encrypting polynomial coefficients...")
        # Encrypt the polynomial coefficients
        self.encrypted_polynomial = self._encrypt_polynomial(self.speed_polynomial_coeffs)
        
        # Store car database (encrypted cars with signatures)
        self.car_database = {}
        self.user_counter = 0
        print("External Program initialization complete!")
        
    def _generate_speed_polynomial(self) -> np.ndarray:
        """Generate random coefficients for the speed polynomial"""
        coeffs = np.random.randint(1, 1000, size=66)
        return coeffs

    def _encrypt_polynomial(self, coeffs: np.ndarray) -> List[PyCtxt]:
        """Encrypt polynomial coefficients"""
        encrypted_coeffs = []
        for coeff in coeffs:
            ctxt = self.HE.encryptInt(np.array([int(coeff)]))
            encrypted_coeffs.append(ctxt)
        return encrypted_coeffs
    
    def get_public_keys(self) -> dict:
        """Export public keys for distribution to server and players"""
        return {
            'signing_public_key': bytes(self.verify_key),
            'he_context': self.HE.to_bytes_context(),
            'he_public_key': self.HE.to_bytes_public_key(),
            'he_relin_key': self.HE.to_bytes_relin_key(),
            'he_rotate_key': self.HE.to_bytes_rotate_key(),
        }
    
    def get_encrypted_polynomial(self) -> List[bytes]:
        """Get encrypted polynomial coefficients for distribution"""
        return [ctxt.to_bytes() for ctxt in self.encrypted_polynomial]
    
    def register_user(self) -> Tuple[int, bytes, bytes]:
        """
        Register a new user and create their first car
        Returns: (user_id, encrypted_car, signature)
        """
        self.user_counter += 1
        user_id = self.user_counter
        
        # Generate random car attributes (10 values between 1 and 999)
        car_attributes = np.array([secrets.randbelow(999) + 1 for _ in range(10)])
        
        # Encrypt the car
        encrypted_car = self._encrypt_car(car_attributes)
        
        # Sign the encrypted car
        signature = self._sign_car(encrypted_car)
        
        # Store in database
        self.car_database[user_id] = {
            'cars': [encrypted_car],
            'signatures': [signature]
        }
        
        return user_id, encrypted_car, signature
    
    # def _encrypt_car(self, attributes: np.ndarray) -> bytes:
    #     """Encrypt car attributes"""
    #     # Encrypt all attributes in a single ciphertext
    #     ctxt = self.HE.encryptInt(attributes.astype(np.int64))
    #     return ctxt.to_bytes()
    def _encrypt_car(self, attributes: np.ndarray) -> bytes:
        encrypted_attrs = []
        for attr in attributes:
            ctxt = self.HE.encryptInt(np.array([int(attr)]))
            encrypted_attrs.append(ctxt.to_bytes())
        return pickle.dumps(encrypted_attrs)
    
    def _sign_car(self, encrypted_car: bytes) -> bytes:
        """Sign an encrypted car with Ed25519 using PyNaCl"""
        signed = self.signing_key.sign(encrypted_car)
        return signed.signature
    
    def verify_signature(self, encrypted_car: bytes, signature: bytes) -> bool:
        """Verify a car's signature using PyNaCl"""
        try:
            self.verify_key.verify(encrypted_car, signature)
            return True
        except nacl.exceptions.BadSignatureError:
            return False
    
    def train_car(self, user_id: int, car_index: int, encrypted_car: bytes, signature: bytes) -> Tuple[bytes, bytes, bool]:
        """Train a car by adding random modifications"""
        if not self.verify_signature(encrypted_car, signature):
            print("Invalid signature!")
            return None, None, False

        # Unpickle to get list of encrypted attributes
        encrypted_attrs = pickle.loads(encrypted_car)
        modifications = np.array([secrets.randbelow(39) - 19 for _ in range(10)])

        new_encrypted_attrs = []
        for i, enc_attr_bytes in enumerate(encrypted_attrs):
            enc_attr = PyCtxt(pyfhel=self.HE, bytestring=enc_attr_bytes)
            enc_mod = self.HE.encryptInt(np.array([int(modifications[i])]))
            enc_new_attr = enc_attr + enc_mod
            new_encrypted_attrs.append(enc_new_attr.to_bytes())

        new_encrypted_car = pickle.dumps(new_encrypted_attrs)
        new_signature = self._sign_car(new_encrypted_car)

        if user_id in self.car_database:
            self.car_database[user_id]['cars'].append(new_encrypted_car)
            self.car_database[user_id]['signatures'].append(new_signature)

        return new_encrypted_car, new_signature, True
    
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
    
    def decrypt_speed(self, encrypted_speed: bytes) -> int:
        """Decrypt a speed value and apply modulo 1001 to ensure positive value"""
        ctxt = PyCtxt(pyfhel=self.HE, bytestring=encrypted_speed)
        speed = self.HE.decryptInt(ctxt)
        # decryptInt returns an array, get the first element and apply modulo 1001
        return int(speed[0]) % 1001
    
    # def decrypt_car(self, encrypted_car: bytes) -> List[int]:
    #     """Decrypt a car (for debugging purposes)"""
    #     ctxt = PyCtxt(pyfhel=self.HE, bytestring=encrypted_car)
    #     decrypted_array = self.HE.decryptInt(ctxt)
    #     return decrypted_array.tolist()
    def decrypt_car(self, encrypted_car: bytes) -> List[int]:
        """Decrypt a car (for debugging purposes)"""
        # Unpickle to get the list of encrypted attribute bytes
        encrypted_attrs = pickle.loads(encrypted_car)
        decrypted = []
        for attr_bytes in encrypted_attrs:
            ctxt = PyCtxt(pyfhel=self.HE, bytestring=attr_bytes)
            val = self.HE.decryptInt(ctxt)
            # decryptInt returns an array, get the first element
            decrypted.append(int(val[0]))
        return decrypted
    
    def save_state(self, filename: str):
        """Save program state to file"""
        state = {
            'signing_key': bytes(self.signing_key),
            'he_secret_key': self.HE.to_bytes_secret_key(),
            'he_context': self.HE.to_bytes_context(),
            'he_public_key': self.HE.to_bytes_public_key(),
            'speed_polynomial': self.speed_polynomial_coeffs.tolist(),
            'encrypted_polynomial': self.get_encrypted_polynomial(),
            'user_counter': self.user_counter
        }
        with open(filename, 'wb') as f:
            pickle.dump(state, f)
    
    def load_state(self, filename: str):
        """Load program state from file"""
        with open(filename, 'rb') as f:
            state = pickle.load(f)
        
        self.signing_key = nacl.signing.SigningKey(state['signing_key'])
        self.verify_key = self.signing_key.verify_key
        
        self.HE = Pyfhel()
        self.HE.from_bytes_context(state['he_context'])
        self.HE.from_bytes_public_key(state['he_public_key'])
        self.HE.from_bytes_secret_key(state['he_secret_key'])
        
        self.speed_polynomial_coeffs = np.array(state['speed_polynomial'])
        self.encrypted_polynomial = [
            PyCtxt(pyfhel=self.HE, bytestring=ctxt_bytes) 
            for ctxt_bytes in state['encrypted_polynomial']
        ]
        
        self.user_counter = state['user_counter']


if __name__ == "__main__":
    print("="*70)
    print("EXTERNAL PROGRAM - STANDALONE TEST")
    print("="*70)
    
    print("\nInitializing...")
    program = ExternalProgram()
    
    print("\n=== User Registration ===")
    user_id, encrypted_car, signature = program.register_user()
    print(f"✓ User {user_id} registered")
    print(f"  Initial car: {program.decrypt_car(encrypted_car)}")
    
    print("\n=== Training ===")
    new_car, new_sig, success = program.train_car(user_id, 0, encrypted_car, signature)
    if success:
        print(f"✓ Training successful")
        print(f"  Trained car: {program.decrypt_car(new_car)}")
        enc_speed = program.calculate_encrypted_speed(new_car)
        speed = program.decrypt_speed(enc_speed)
        print(f"  Speed: {speed}")
    
    print("\n=== Saving State ===")
    program.save_state("program_state.pkl")
    print("✓ State saved")
