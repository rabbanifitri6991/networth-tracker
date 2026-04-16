# 💰 Net Worth Tracker

A personal finance web app for tracking your monthly net worth — assets, liabilities, goals, and more. Each user has their own private account and data.

Built with **Streamlit**, **Supabase** (PostgreSQL + Auth), and **Plotly**.

🔗 **Live demo:** *(paste your Streamlit Cloud URL here after deploying)*

---

## Features

- 🔐 **Accounts** — Sign up / sign in with email & password (Google OAuth optional)
- 📊 **Live Net Worth Widget** — see your total wealth at a glance
- 📅 **Monthly Asset Updates** — Excel-style table to update all values each month
- 🗂 **Asset Categories** — Cash & Savings, Investments, Crypto & Gold, Property, EPF/Retirement
- 📉 **Liability Tracking** — Home Loan, Car Loan, Credit Card, Student Loan (PTPTN)
- 📈 **Net Worth Charts** — line chart, assets vs liabilities, category donut
- 🎯 **Goals Tracker** — set financial targets and track progress visually
- ⏳ **Savings Runway** — "How long will my money last?" calculator
- 🌐 **Multi-language** — English (full), Japanese (stubs ready)
- 💱 **Multi-currency** — RM, USD, JPY, SGD (XE.com integration ready)

---

## Tech Stack

| Layer | Tool |
|-------|------|
| UI | [Streamlit](https://streamlit.io) |
| Database | [Supabase](https://supabase.com) (PostgreSQL) |
| Auth | Supabase Auth (email/password + Google OAuth) |
| Charts | [Plotly](https://plotly.com/python/) |
| Hosting | [Streamlit Community Cloud](https://streamlit.io/cloud) |

---

## Setup Guide

### Step 1 — Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Click **New Project**, choose a name and password
3. Wait ~2 minutes for the project to be ready

### Step 2 — Create the database tables

1. In your Supabase project, go to **SQL Editor → New Query**
2. Copy the entire contents of `supabase_schema.sql`
3. Paste it and click **Run**

You should see all 5 tables created: `assets`, `asset_values`, `liabilities`, `liability_values`, `goals`.

### Step 3 — Get your API credentials

In your Supabase project go to **Project Settings → API**:

- Copy **Project URL** → this is your `SUPABASE_URL`
- Copy **anon / public** key → this is your `SUPABASE_ANON_KEY`

### Step 4 — Run locally

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/networth-tracker.git
cd networth-tracker

# Create a virtual environment
python -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Set up credentials
cp .env.example .env
# Edit .env and paste your SUPABASE_URL and SUPABASE_ANON_KEY

# Run the app
streamlit run app.py
```

Open `http://localhost:8501` in your browser. Sign up with your email and start tracking!

---

## Deploying to Streamlit Community Cloud (free)

### Step 1 — Push to GitHub
Make sure your code is pushed to a GitHub repository.

### Step 2 — Connect to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Select your repo → branch: `main` → main file: `app.py`
5. Click **Deploy**

### Step 3 — Add secrets

After deployment, go to **App → Settings → Secrets** and paste:

```toml
SUPABASE_URL = "https://your-project-id.supabase.co"
SUPABASE_ANON_KEY = "your-anon-public-key"
SITE_URL = "https://your-app-name.streamlit.app"
```

Your app will automatically redeploy with the secrets configured.

---

## Enabling Google Sign-In (optional)

1. In Supabase → **Authentication → Providers → Google** → Enable it
2. Create a Google OAuth app at [console.cloud.google.com](https://console.cloud.google.com):
   - Create a project → APIs & Services → Credentials → OAuth 2.0 Client ID
   - Add your Streamlit Cloud URL as an **Authorized redirect URI**:
     `https://your-project-id.supabase.co/auth/v1/callback`
3. Copy the **Client ID** and **Client Secret** back into Supabase → Google provider settings
4. In Streamlit secrets, make sure `SITE_URL` is set to your live app URL

---

## Adding a New Language

1. Open `i18n/translations.py`
2. Add a new key to `SUPPORTED_LANGUAGES` (e.g. `"Bahasa Melayu": "ms"`)
3. Add a matching dictionary under `TRANSLATIONS["ms"]` with the same keys as `"en"`
4. The language appears automatically in the sidebar dropdown

---

## Currency Conversion (XE.com)

Live currency rates via XE.com are stubbed and ready. To enable:

1. Sign up at [xe.com/xecurrencydata](https://www.xe.com/xecurrencydata/)
2. Add to your `.env` or Streamlit secrets:
   ```
   XE_ACCOUNT_ID=your_account_id
   XE_API_KEY=your_api_key
   ```
3. Uncomment the live fetch section in `utils/currency.py`

---

## Project Structure

```
networth-tracker/
├── app.py                      # Streamlit entry point + navigation
├── database.py                 # All Supabase DB operations
├── supabase_client.py          # Supabase client + auth helpers
├── supabase_schema.sql         # Run once in Supabase SQL editor
├── requirements.txt
├── .env.example                # Credentials template (copy to .env)
├── .gitignore
│
├── .streamlit/
│   └── secrets.toml.example    # Streamlit Cloud secrets template
│
├── components/
│   ├── auth.py                 # Login / sign-up page
│   ├── dashboard.py            # Live net worth widget + mini chart
│   ├── assets.py               # Asset management & monthly update
│   ├── liabilities.py          # Liabilities management
│   ├── networth.py             # Net worth history charts
│   ├── goals.py                # Financial goals tracker
│   └── how_long.py             # Savings runway calculator
│
├── i18n/
│   ├── __init__.py
│   └── translations.py         # English + Japanese text strings
│
└── utils/
    ├── currency.py             # Currency conversion (XE.com ready)
    └── formatters.py           # Number & date formatting
```

---

## Roadmap

- [ ] Complete Japanese translations
- [ ] XE.com live currency rates
- [ ] Bahasa Melayu language
- [ ] CSV / Excel export
- [ ] Email reminders for monthly updates
- [ ] Mobile-responsive improvements
- [ ] future improvements for privacy
        - Encrypt data before storing — store values as encrypted text so even you can't read the numbers without the user's key. Very secure but complex to build.
        - Restrict admin access — set internal rules that developers can't query user data without approval.
        - Write a clear Privacy Policy — at minimum, tell users honestly what you can see.

---

## License

MIT — free to use and modify.
