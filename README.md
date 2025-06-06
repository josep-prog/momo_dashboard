# MTN MoMo Dashboard

A simple yet effective dashboard for analyzing MTN Mobile Money (MoMo) transaction data from SMS messages.

## Features

- Parse and process SMS data from XML files
- Store transaction data in SQLite database
- Interactive dashboard with:
  - Transaction search and filtering
  - Date range selection
  - Transaction type filtering
  - Visual charts for transaction analysis
  - Detailed transaction view

## Requirements

- Python 3.6+
- Flask
- SQLite3

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd momo_dashboard
```

2. Install the required packages:
```bash
pip install flask
```

3. Place your SMS XML file in the project directory as `modified_sms_v2.xml`

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
momo_dashboard/
├── app.py              # Main Flask application
├── schema.sql          # Database schema
├── modified_sms_v2.xml # SMS data file
├── static/
│   └── styles.css      # CSS styles
└── templates/
    └── index.html      # Dashboard template
```

## Data Processing

The application processes SMS messages and categorizes them into:
- Received Money
- Payments
- Bank Deposits
- Withdrawals
- Internet Bundles
- Cash Power

Each transaction is stored with:
- Transaction type
- Amount
- Person/Recipient
- Date
- Transaction ID
- Fee (if applicable)

## License

MIT License
