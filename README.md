# QR Guests

windows app built with OpenCV + pyzbar to scan qr code and take a photo then fill presence in SQLite database. 

## Installation

Firstly you need to clone this repository, to install requirements use the package manager [pip](https://pip.pypa.io/en/stable/).

```bash
pip install -r requirements.txt
```

## Usage

1. Set your folder to store photo in app.py
2. Create .db file in this repository then set the database connection and table name in ```class Database``` to your database.
3. Make sure you have generated hash code from names column in database table and convert hash to qrcode (this feature will be added ASAP :))
4. run in cmd ```python app.py```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
