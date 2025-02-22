## Windows

1. Clone repository
```bash
git clone https://github.com/Amarudinn/monad.git
cd monad
```

2. Edit file .env

3. Install dependencies
```bash
pip install requirements.txt
```

4. Run script
```bash
python main.py
```

## Linux/VPS

1. Clone repository
```bash
git clone https://github.com/Amarudinn/monad.git
```

2. Buat screen
```bash
screen -S monad-testnet
```

3. Open file
```bash
cd monad
```

4. Edit file .env
```bash
nano .env
```

5. Buat enviroment
```bash
python3 -m venv venv
source venv/bin/activate
```

6. Install dependencies
```bash
pip install requirements.txt
```

7. Run script
```bash
python3 main.py
```

8. Minimize screen CTRL A+D

9. Open screen
```bash
screen -r monad-testnet
```
