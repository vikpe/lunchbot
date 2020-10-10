# lunchbot ![test](https://github.com/vikpe/lunchbot/workflows/test/badge.svg?branch=master)
> A Discord bot for coordinating lunches

## Development

### Setup

**Clone repo**
```bash
git clone https://github.com/stedo880/lunchbot.git
cd lunchbot
```

**Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Install dependencies**
```bash
python -m pip install -r requirements.txt -r requirements_dev.txt 
```

### Run tests
```bash
python -m pytest tests.py --cov --disable-warnings
```

### Code formatting (black)
```bash
black .
```
