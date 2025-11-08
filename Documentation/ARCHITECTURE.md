# F1-AI Racing Game - System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TRUSTED ZONE                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              EXTERNAL PROGRAM                                  │  │
│  │                                                                │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐               │  │
│  │  │ Ed25519  │  │   BFV    │  │    Speed     │               │  │
│  │  │  Keys    │  │   Keys   │  │  Polynomial  │               │  │
│  │  │  (f1,v1) │  │(p1,p2,p3)│  │   (Secret)   │               │  │
│  │  └────┬─────┘  └────┬─────┘  └──────┬───────┘               │  │
│  │       │             │                │                        │  │
│  │       └─────────────┴────────────────┘                        │  │
│  │                     │                                         │  │
│  │             ┌───────▼────────┐                                │  │
│  │             │  Key Manager   │                                │  │
│  │             │   Decryption   │                                │  │
│  │             └───────┬────────┘                                │  │
│  └─────────────────────┼─────────────────────────────────────────┘  │
└────────────────────────┼──────────────────────────────────────────────┘
                         │
         Public Keys (v1, p1, p2, p3) + Encrypted Polynomial
                         │
         ┌───────────────┼───────────────────┐
         │               │                   │
    ┌────▼──────┐   ┌────▼──────┐    ┌──────▼────────┐
    │  PLAYER 1 │   │  SERVER   │    │  BLOCKCHAIN   │
    │           │   │           │    │               │
    │  Cars: [] │   │  Races    │    │  Smart        │
    │  XPF: 10  │   │  Verify   │    │  Contract     │
    └─────┬─────┘   └─────┬─────┘    └───────┬───────┘
          │               │                   │
    ┌─────▼─────┐   ┌─────▼─────┐    ┌───────▼───────┐
    │  PLAYER 2 │   │  PLAYER 3 │    │  Public       │
    │           │   │           │    │  Ledger       │
    │  Cars: [] │   │  Cars: [] │    │  (Verifiable) │
    │  XPF: 10  │   │  XPF: 10  │    └───────────────┘
    └───────────┘   └───────────┘
```

## Data Flow

### 1. Registration Phase

```
Player                External Program              Blockchain
  │                          │                          │
  │───Register Request──────►│                          │
  │                          │                          │
  │                          │──Generate Random Car────►│
  │                          │  (t0..t9 ∈ [1,999])     │
  │                          │                          │
  │                          │──Encrypt Car─────────────►│
  │                          │  Enc(t0)...Enc(t9)       │
  │                          │                          │
  │                          │──Sign Car────────────────►│
  │                          │  Sig = Sign_f1(Enc(car)) │
  │                          │                          │
  │◄──(Enc(car), Sig)────────│                          │
  │                          │                          │
  │                          │                          │
  │──────Register Tx──────────────────────────────────►│
  │      (user_id)                                      │
  │                                                     │
  │◄─────10 XPF Credited────────────────────────────────│
  │                                                     │
```

### 2. Training Phase

```
Player                External Program              Server
  │                          │                         │
  │──Pay 1 XPF───────────────┼────────────────────────►│
  │                          │                         │
  │──(Enc(car), Sig)────────►│                         │
  │                          │                         │
  │                          │──Verify Sig─────────────►│
  │                          │  ✓                      │
  │                          │                         │
  │                          │──Generate Δt ∈ [-19,19]►│
  │                          │                         │
  │                          │──Homomorphic Add────────►│
  │                          │  Enc(t') = Enc(t) + Enc(Δt)
  │                          │                         │
  │◄──(Enc(car'), Sig')──────│                         │
  │                          │                         │
  │──Calculate Speed────────►│                         │
  │  Enc(speed) = P(Enc(car))│                         │
  │                          │                         │
  │──Decrypt Request────────►│                         │
  │                          │                         │
  │◄──speed value────────────│                         │
  │                          │                         │
```

### 3. Racing Phase

```
Player              Server              External Program    Blockchain
  │                   │                        │                │
  │──Pay 1 XPF────────┼───────────────────────►│───────────────►│
  │                   │                        │                │
  │──Submit Entry────►│                        │                │
  │  (Enc(car), Sig)  │                        │                │
  │                   │                        │                │
  │                   │──Verify Sig───────────►│                │
  │                   │  ✓                     │                │
  │                   │                        │                │
  │                   │──Calculate All Speeds─►│                │
  │                   │  Enc(s1), Enc(s2)...   │                │
  │                   │                        │                │
  │                   │──Decrypt Speeds───────►│                │
  │                   │                        │                │
  │                   │◄──s1, s2, s3...────────│                │
  │                   │                        │                │
  │                   │──Determine Winner──────►│                │
  │                   │                        │                │
  │                   │──Publish Results───────┼───────────────►│
  │                   │  winner_id, speeds     │                │
  │                   │                        │                │
  │◄──100 XPF (if win)┼────────────────────────┼───────────────►│
  │                   │                        │                │
```

## Cryptographic Operations

### Car Encryption

```
Plaintext Car:     [t0, t1, t2, t3, t4, t5, t6, t7, t8, t9]
                    ↓    ↓    ↓    ↓    ↓    ↓    ↓    ↓    ↓    ↓
Encrypt with p1:   [E0, E1, E2, E3, E4, E5, E6, E7, E8, E9]
                    ↓
Sign with f1:      Signature
                    ↓
Result:            (Encrypted Car, Signature)
```

### Speed Calculation

```
Speed Polynomial (66 coefficients):
  P(t0..t9) = c0                           (1 term)
            + c1·t0 + ... + c10·t9         (10 terms)
            + c11·t0² + ... + c20·t9²      (10 terms)
            + c21·t0·t1 + c22·t0·t2 + ...  (45 terms)

Homomorphic Evaluation:
  Enc(speed) = Enc(c0)
             + Enc(c1)·Enc(t0) + ... + Enc(c10)·Enc(t9)
             + Enc(c11)·Enc(t0)·Enc(t0) + ...
             + Enc(c21)·Enc(t0)·Enc(t1) + ...
```

### Training Modification

```
Original:         Enc(t0), Enc(t1), ..., Enc(t9)
                     ↓        ↓              ↓
Generate Δ:       Δ0∈[-19,19], Δ1, ..., Δ9
                     ↓        ↓              ↓
Encrypt:          Enc(Δ0), Enc(Δ1), ..., Enc(Δ9)
                     ↓        ↓              ↓
Homomorphic Add:  Enc(t0+Δ0), Enc(t1+Δ1), ..., Enc(t9+Δ9)
                     ↓        ↓              ↓
New Car:          [E'0, E'1, E'2, ..., E'9]
```

## Security Properties

### Confidentiality

```
Player View:
  Own Car:     ⊗ Encrypted (cannot see plaintext)
  Other Cars:  ⊗ Encrypted (cannot see plaintext)
  Speed Formula: ⊗ Encrypted (cannot see coefficients)
  Own Speed:   ✓ Decrypted (after training/race)

Server View:
  All Cars:    ⊗ Encrypted (only public key)
  Speed Formula: ⊗ Encrypted (only public key)
  Speeds:      ✓ Encrypted → Decrypted by External Program
  
External Program View:
  All Cars:    ✓ Can decrypt (has private key k1)
  Speed Formula: ✓ Knows plaintext (generated it)
  Purpose:     Trusted oracle for decryption only
```

### Integrity

```
Signature Verification Flow:
  1. Player receives (Enc(car), Sig)
  2. Server receives entry
  3. Server verifies: Verify_v1(Enc(car), Sig) = ✓
  4. If verification fails → reject entry
  5. Blockchain stores (Enc(car), Sig) publicly
  6. Anyone can verify signature later
```

### Verifiability

```
Race Verification:
  1. Server publishes (Enc(car_i), speed_i) for all participants
  2. Anyone can re-calculate: Enc(speed_i) = P(Enc(car_i))
  3. Compare: Enc(speed_i) ?= Encrypt(speed_i)
  4. If mismatch → server cheated → cancel race
  5. Smart contract handles refunds automatically
```

## Token Flow

```
           ┌──────────────┐
           │   10 XPF     │  ← Initial Balance
           └──────┬───────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼────┐      ┌─────▼─────┐
    │ -1 XPF  │      │  -1 XPF   │
    │Training │      │   Race    │
    │ (9x)    │      │ Entry     │
    └────┬────┘      └─────┬─────┘
         │                 │
    ┌────▼────┐      ┌─────▼─────┐
    │ Result: │      │  If Win:  │
    │  0 XPF  │      │ +100 XPF  │
    └─────────┘      └───────────┘
                           │
                     ┌─────▼─────┐
                     │ Total:    │
                     │ 100 XPF   │
                     └───────────┘
```

## Component Interactions

```
┌─────────────┐
│   Player    │
└──────┬──────┘
       │ 1. Calculate Enc(speed) locally
       │    using public keys
       │
       ▼
┌─────────────┐
│   Server    │
└──────┬──────┘
       │ 2. Verify signature
       │ 3. Calculate Enc(speed) again
       │ 4. Request decryption
       │
       ▼
┌─────────────┐
│  External   │
│  Program    │
└──────┬──────┘
       │ 5. Decrypt all speeds
       │ 6. Return plaintext values
       │
       ▼
┌─────────────┐
│   Server    │
└──────┬──────┘
       │ 7. Determine winner
       │ 8. Publish to blockchain
       │
       ▼
┌─────────────┐
│ Blockchain  │
└──────┬──────┘
       │ 9. Distribute prize
       │ 10. Store immutable record
       │
       ▼
    [Anyone]
       │ 11. Verify results
       └─────► Compare Enc(speeds)
```

## File Organization

```
f1-ai-racing/
│
├── Core Implementation
│   ├── external_program.py     [Trusted] Key manager
│   ├── player.py               [Untrusted] Client
│   ├── server.py               [Untrusted] Race manager
│   └── blockchain_interface.py [Public] Web3 bridge
│
├── Smart Contract
│   └── F1AIRacing.sol          [Public] On-chain logic
│
├── Demo & Tests
│   └── demo.py                 Complete workflow
│
├── Documentation
│   ├── README.md               Full documentation
│   ├── DEPLOYMENT.md           Setup guide
│   ├── SUMMARY.md              Project overview
│   └── ARCHITECTURE.md         This file
│
└── Configuration
    └── requirements.txt        Dependencies
```

---

**Legend:**
- ✓ : Allowed/Visible
- ⊗ : Blocked/Encrypted
- → : Data flow
- ◄ : Response
