# F1-AI Racing Game - Complete Implementation

**🐳 Now with Docker support for easy Windows installation!**

A secure racing game using homomorphic encryption (BFV), digital signatures (Ed25519 via PyNaCl), and blockchain technology.

## 🚀 Quick Start

### For Windows Users (Recommended)

See **[QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)** for a 5-minute setup guide using Docker!

```bash
# 1. Install Docker Desktop
# 2. Run these commands:
docker-compose build
docker-compose up
```

### For Linux/Mac Users

#### Option 1: Docker (Easiest)
```bash
docker-compose build
docker-compose up
```

#### Option 2: Native Installation
```bash
pip install -r requirements.txt
python demo.py
```

## 📋 What's New

### ✅ Docker Support
- Solves Pyfhel installation issues on Windows
- Consistent environment across all platforms
- No manual dependency installation needed
- See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for details

### ✅ PyNaCl for Ed25519
- Replaced `cryptography` library with `PyNaCl`
- Faster signature operations
- Simpler API
- Better cross-platform support

## 🎮 What This Does

Implements a cryptographic racing game where:
- **Cars** have 10 encrypted attributes (flags) - nobody can see them!
- **Speed** is calculated using a secret encrypted polynomial
- **Training** modifies cars using homomorphic encryption
- **Racing** is fair and verifiable on blockchain
- **Cheating** is cryptographically impossible

## 🔐 Security Features

✅ **Homomorphic Encryption (BFV)**: Compute on encrypted data  
✅ **Ed25519 Signatures (PyNaCl)**: Verify car authenticity  
✅ **Secret Speed Formula**: Encrypted 66-coefficient polynomial  
✅ **Blockchain Verification**: Transparent, immutable results  
✅ **Zero Trust**: Server can't cheat, players can't modify cars  

## 📦 Files Included

### Core Implementation
- `external_program.py` - Trusted key manager (Ed25519 + BFV)
- `player.py` - Player client (car management, racing)
- `server.py` - Race server (verification, results)
- `demo.py` - Complete workflow demonstration

### Smart Contract
- `F1AIRacing.sol` - Solidity contract for blockchain

### Docker Setup
- `Dockerfile` - Container image definition
- `docker-compose.yml` - Easy orchestration
- `.dockerignore` - Build optimization

### Documentation
- `README_DOCKER.md` - This file
- `QUICKSTART_WINDOWS.md` - 5-minute Windows guide
- `DOCKER_GUIDE.md` - Detailed Docker documentation
- `DEPLOYMENT.md` - Production deployment guide
- `ARCHITECTURE.md` - System design diagrams

## 🎯 Game Mechanics

### Token Economy
- **Start**: 10 XPF per player
- **Training**: -1 XPF (modify car by ±19 per attribute)
- **Race Entry**: -1 XPF
- **Win Prize**: +100 XPF

### Workflow
1. Register (get encrypted car)
2. Train 9 times (improve speed)
3. Enter race (pay 1 XPF)
4. Server calculates encrypted speeds
5. External program decrypts speeds
6. Winner gets 100 XPF
7. Results verified on blockchain

## 🔬 Technical Details

### Cryptography
- **Ed25519 (PyNaCl)**: 256-bit signatures, ~128-bit security
- **BFV Homomorphic Encryption**: n=8192, t=65537
- **Speed Polynomial**: Degree 2, 10 variables, 66 coefficients

### Performance
- Key generation: ~5-10 seconds
- Car encryption: ~100 ms
- Training: ~200-300 ms
- Speed calculation: ~1-2 seconds
- Signature: <10 ms

### Dependencies
```txt
Pyfhel==3.4.2      # Homomorphic encryption
PyNaCl==1.5.0      # Ed25519 signatures
numpy==1.24.3       # Numerical operations
web3==6.11.3        # Blockchain integration
```

## 📖 Usage Examples

### Docker (Recommended)

```bash
# Run complete demo
docker-compose up

# Interactive mode
docker-compose --profile dev up -d f1ai-dev
docker exec -it f1ai-dev /bin/bash
python3 demo.py

# Clean up
docker-compose down
```

### Native Python

```python
from external_program import ExternalProgram
from player import Player
from server import Server

# Initialize
program = ExternalProgram()
keys = program.get_public_keys()
poly = program.get_encrypted_polynomial()

# Register player
user_id, car, sig = program.register_user()
player = Player(user_id, keys, poly)
player.add_car(car, sig)

# Train car
player.train_car(0, program)

# Enter race
server = Server(keys, poly)
server.accept_race_entry(user_id, car, sig)
results = server.run_race(program)
```

## 🏗️ Architecture

```
┌─────────────────────┐
│  External Program   │  ← Trusted (has private keys)
│   (Key Manager)     │
└──────────┬──────────┘
           │
           ├─────────┬─────────┐
           │         │         │
      ┌────▼───┐ ┌───▼────┐ ┌─▼─────────┐
      │Player 1│ │ Server │ │Blockchain │
      └────────┘ └────────┘ └───────────┘
```

## 🧪 Testing

```bash
# Run complete demo
python demo.py

# Test components individually
python external_program.py

# With Docker
docker-compose run --rm f1ai-game python3 demo.py
```

## 🚢 Deployment

### Local Testing
```bash
docker-compose up
```

### Production
```bash
# See DEPLOYMENT.md for full guide
docker build -t f1ai-racing .
docker run -d -v /data/output:/app/output f1ai-racing
```

### Smart Contract
```bash
# Compile
solc --optimize --bin --abi F1AIRacing.sol -o build/

# Deploy using Remix, Hardhat, or Truffle
```

## 🐛 Troubleshooting

### Pyfhel Won't Install (Windows)
**Solution**: Use Docker! See [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)

### Docker Build Fails
```bash
docker-compose build --no-cache
```

### Permission Errors
```bash
# Linux/Mac
sudo docker-compose up

# Windows: Run PowerShell as Administrator
```

### Module Not Found
```bash
# Native installation
pip install -r requirements.txt

# Docker: rebuild
docker-compose build
```

## 📚 Documentation

- **[QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)** - 5-minute Windows setup
- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - Complete Docker documentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design
- **[SUMMARY.md](SUMMARY.md)** - Project overview

## 🔄 Updates from Original

### Changed
- ✅ `cryptography` → `PyNaCl` for Ed25519
- ✅ Added complete Docker support
- ✅ Created Windows quick start guide

### Added
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ .dockerignore
- ✅ Detailed Docker documentation
- ✅ Windows-specific guides

### Improved
- ✅ Cross-platform compatibility
- ✅ Easier installation process
- ✅ Better documentation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test with Docker: `docker-compose up`
5. Submit pull request

## 📜 License

Educational and hackathon use. For production, conduct security audit.

## 🙏 Acknowledgments

- IXH25 Hackathon Challenge
- De Componendis Cifris Association
- Pyfhel Library (Alberto Ibarrondo)
- PyNaCl (NaCl/libsodium)

## 📞 Support

### For Docker Issues
See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) troubleshooting section

### For Windows Issues
See [QUICKSTART_WINDOWS.md](QUICKSTART_WINDOWS.md)

### For General Questions
Check [SUMMARY.md](SUMMARY.md) and [ARCHITECTURE.md](ARCHITECTURE.md)

---

**🐳 Docker makes everything easier - especially on Windows!**

**🎉 Now you can run the full cryptographic racing game without any installation headaches!**
