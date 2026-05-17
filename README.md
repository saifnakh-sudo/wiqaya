# WIQAYA -- AI-Powered Post-Breach Identity Shield
> © 2026 Ahmed Saifeddine Nakhli / LUMIVYN LTD · All Rights Reserved  
> Proprietary software. Viewing permitted for portfolio evaluation only.  
> Unauthorized use, cloning, or reproduction is strictly prohibited.

> Youth Nexus Cyber AI Challenge -- 1ere Edition
> ENSA Kenitra x CMRPI -- Mai 2026

## Description

WIQAYA is an AI-powered post-breach cybersecurity tool designed for Moroccan citizens affected by the CNSS breach (April 2025, ~2M citizens) and the OFPPT breach (April 2026, 400K+ students).

### Three modules:

1. **Breach Exposure Scanner** -- Check if your data (CIN/email) appears in known breaches
2. **AI Protection Plan** -- Personalized action plan based on Moroccan law (Loi 09-08, 05-20)
3. **Phishing Simulator** -- Learn to detect targeted scams exploiting your exposed data

## Installation

### Prerequisites
- Python 3.10+
- OpenAI API key (for modules 2 and 3)

### Steps

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set the OpenAI API key
# Windows PowerShell:
$env:OPENAI_API_KEY="sk-your-key-here"
# Mac/Linux:
export OPENAI_API_KEY="sk-your-key-here"

# 3. (Optional) Regenerate the synthetic database
python seed_database.py

# 4. Run the application
python app.py
```

Open http://localhost:5000 in your browser.

### Important note
The database contains 5,000 synthetic records. No real personal data is used.

## Tech Stack

| Component  | Technology         |
|------------|--------------------|
| Backend    | Python + Flask     |
| Database   | SQLite             |
| AI         | OpenAI GPT-4o      |
| Frontend   | HTML / CSS / JS    |
| Languages  | French / Arabic    |

## Project Structure

```
wiqaya/
-- app.py              Flask server + API endpoints
-- seed_database.py    Synthetic data generator
-- requirements.txt    Python dependencies
-- wiqaya.db           SQLite database
-- templates/
   -- index.html       Main interface
-- static/
   -- css/style.css    Stylesheet
   -- js/app.js        Frontend logic
```

## Legal Framework

WIQAYA references:
- Loi 09-08 -- Personal data protection
- Loi 05-20 -- Cybersecurity
- CNDP -- National Data Protection Commission
- DGSSI -- General Directorate of Information Systems Security

---

ENSA Kenitra -- Universite Ibn Tofail -- Mai 2026
