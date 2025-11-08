# F1-AI Racing Game - Quick Start

## 🚀 Launch in 30 Seconds

### Windows
```bash
start-web-ui.bat
```

### Linux/Mac
```bash
chmod +x start-web-ui.sh
./start-web-ui.sh
```

### Manual
```bash
docker-compose up f1ai-web
```

Then open: **http://localhost:5000**

---

## 🎮 How to Play

### 1️⃣ Register (Free)
- Click "Register & Start Playing"
- Get User ID + 10 XPF tokens
- Receive encrypted car with speed

### 2️⃣ Train Your Car (1 XPF)
- Click "Train" on any car
- Attributes change by ±19
- Speed recalculated (may go up or down)
- Can train multiple times

### 3️⃣ Race (1 XPF entry, 100 XPF prize)
- Click "Race" on your best car
- Compete against 2 AI opponents
- Highest speed wins
- Winner gets 100 XPF tokens

---

## 💡 Strategy Tips

1. **Train First**: Build up speed before racing
2. **Save Tokens**: Keep at least 1 XPF for racing
3. **Multiple Cars**: Training creates new car versions
4. **Win Races**: Only way to earn more tokens (100 XPF)

---

## 🔧 Common Commands

### Start Web UI
```bash
docker-compose up f1ai-web
```

### Stop Server
```bash
Ctrl+C or docker-compose down
```

### Rebuild
```bash
docker-compose build f1ai-web
```

### View Logs
```bash
docker-compose logs -f f1ai-web
```

### CLI Demo (Old Way)
```bash
docker-compose --profile cli up f1ai-game
```

---

## 📊 Game Stats

| Item | Amount |
|------|--------|
| Starting XPF | 10 |
| Training Cost | 1 XPF |
| Race Entry Fee | 1 XPF |
| Race Prize (Win) | 100 XPF |
| Car Attributes | 10 |
| Speed Range | 0-1000 |
| Race Opponents | 2 |

---

## 🐛 Troubleshooting

### "Cannot connect to server"
```bash
# Check if Docker is running
docker ps

# Restart container
docker-compose restart f1ai-web
```

### "Port already in use"
Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:5000"  # Change 5000 to 8080
```

### "Build failed"
```bash
# Clean rebuild
docker-compose build --no-cache f1ai-web
```

---

## 📚 Documentation

- **[README.md](README.md)** - Full documentation
- **[WEB_UI_GUIDE.md](WEB_UI_GUIDE.md)** - Detailed web UI guide
- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - Docker setup help
- **[CHANGES.md](CHANGES.md)** - What's new

---

## ✨ Key Features

- 🔐 **Homomorphic Encryption** - Cars always encrypted
- ✍️ **Digital Signatures** - Tamper-proof
- 🎨 **Modern UI** - Beautiful React interface
- 🏁 **Fair Racing** - Modulo 1001 ensures positive speeds
- 💰 **Token Economy** - Train, race, earn
- 📱 **Responsive** - Works on desktop and mobile

---

## 🎯 Quick Example

```bash
# 1. Start server
docker-compose up f1ai-web

# 2. Open browser
# Navigate to http://localhost:5000

# 3. Play!
# - Register (get 10 XPF)
# - Train 3 times (cost 3 XPF, 7 remaining)
# - Race (cost 1 XPF, 6 remaining)
# - If you win: +100 XPF = 106 total!
# - If you lose: Keep training and try again
```

---

## 🏆 Winning Strategy

Best approach for beginners:

1. **Register** - Start with 10 XPF
2. **Train 5 times** - Cost 5 XPF, balance = 5 XPF
3. **Check speed** - If > 500, good to race
4. **Race** - Cost 1 XPF, balance = 4 XPF
5. **If win** - Get 100 XPF, new balance = 104 XPF
6. **Repeat** - Keep training best cars and racing

---

**Ready? Start playing now!** 🏎️💨
