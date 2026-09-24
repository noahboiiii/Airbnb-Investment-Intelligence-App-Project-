# Airbnb-Investment-Intelligence-App-Project-
We are working as part of a data &amp; AI consulting team supporting a property investor who wants to make a more informed Airbnb investment decision. We will design, build, deploy, and present a data-driven Airbnb Investment Intelligence App that helps a user explore where, what, and how to invest in short term rental property across UK cities. 

Public Deployed App Link: 

## Key Features
- City Selector
- Investment Recommendation
- Transparent Scoring Model
- Short-Term vs Long-Term Yield Comparison
- AI Review Intelligence & Sentiment Analysis
- Regulatory Risk & Compliance Notes
- Executive Memo Export

## Exact Investment Scoring Formula
Investment Score (0-100) ranking areas, property types, and listings is calcullated dynamically using a transparent 5-factor weighting model:

1) Gross Revenue Proxy (30%): Estimated annual revenue dervied from nightly prices multiplied by unavailiable calendar days
2) Occupancy Stability (25%): Minimum availiability consistency across a 12-month snapshot window
3) Guest Sentiment & Rating (20%): Weighted score combining average review ratings and total review volumes
Short-Term vs Long-Term Yield Spread (15%): Outperformance margin against local baseline benchmarks
Regulatory & Planning Risk (10%): Penalty applied to areas with strict short-term let enforcement or caps

## Investor Personas
The platform dynamically adapts its metric framing, weighting logic and recommendations based on three distinct user profiles:

- Revenue Maximiser: Prioritises top-line gross yield potential and highest Average Daily Rate (ADR)
- Risk-Averse Investor: Focuses heavily on consistent occupancy proxises, high review volumes and strict regulatory compliance
- Balanced Investor: Applies an equalised weighting across occupancy stability, nightly yield, guest sentiment and regulatory risks

## Data Sources
- Primary Dataset: Inside Airbnb (detailed listings, calendar data, reviews, summary metrics, and neighbourhood files)

## Technology Stack
- Frontend & UI: Python, Streamlit
- Data Manipulation: Python, NumPy
- Data Platform & Storage: Snowflake using secure cryptographic private key authentication
- AI Provider: Snowflake Cortex AI running 'llama3.1-70b'
- Version Control: GitHub

# Local Setup
1) Clone the repository
   ```bash 
   git clone -b noah-ui --single-branch https://github.com/noahboiiii/Airbnb-Investment-Intelligence-App-Project-.git
   ```
2) Install dependencies
   ```bash
    pip install -r requirements.txt
    ```
3) Create an encrypted private key by opening the terminal and running the following, making sure to enter a secure password when prompted:
   ```bash
   openssl genrsa 2048 | openssl pkcs8 -topk8 -v2 des3 -inform PEM -out rsa_key.p8
   ```
   Extract the public key and assign it to your Snowflake account
   Extract the public key:
   ```bash
   openssl rsa -in rsa_key.p8 -pubout -out rsa_key.pub
   ```
   Assign the public key to your snowflake account
   ```bash
   ALTER USER YOUR_USER SET RSA_PUBLIC_KEY='<copied_public_key_string_without_headers>';
   ```
5) Create a hidden folder named .streamlit and a file named secrets.toml to securely handle your snowflake connection and key-pair authentication:
    ```bash
    [connections.snowflake]
    account = "your_account"
    user = "your_user"
    role = "your_role"
    warehouse = "your_warehouse"
    database = "AIRBNB_DB"
    schema = "CLEAN"
    
    [private_key_pem]
    "-----BEGIN PRIVATE KEY-----\n..."
    ```
    
    [private_key_passphrase]
    "your_passphrase"
6) Run the streamlit application
   ```bash
   streamlit run streamlit_app.py
   ```

## Project Structure
```text
📦 Airbnb-Investment-Intelligence-App-Project/
├── .streamlit/
│   └── config.toml           # Local app config & credentials connection (git-ignored)
├── pyproject.toml            # Python project metadata & build config
├── README.md                 # Project documentation and setup guide
├── requirements.txt          # Python package dependencies
├── snowflake.yml             # Snowflake deployment & app configuration
└── streamlit_app.py          # Main Streamlit application source code
```


## Team Members
Noah Esguerra - Data Cleaning, AI implementation, app development

Thomas Hughes - Raw Data Ingestion

Teanna Ottey - Github and Snowflake account creation