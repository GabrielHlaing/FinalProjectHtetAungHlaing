### INF601 - Advanced Programming in Python
### Htet Aung Hlaing
### Final Project

# Project Title
Multi-currency Money Tracker

A simple yet powerful personal finance tracker built with **Python**, **Streamlit**, and **SQLite**.  
It supports multiple currencies using live conversion rates and provides visual dashboards for income, expenses, and category breakdowns.

## Features
 
- Dashboard with:
  - Category breakdown (colored by income/expense)
  - Monthly income vs expense chart
  - Net balance trend chart
  - Next-month forecast
- Add, view, edit, and delete transactions  
- Multi-currency support with live exchange rate conversion 
- Settings system with persistent base currency
- Clean UI using Streamlit components

## Tech Stack

- **Python**
- **Streamlit**
- **Plotly Express**
- **SQLite** (via custom database layer)
- **Requests** (for live currency API)
- Modular architecture (core/, api/, tabs/)

## Project Structure
```
MoneyTracker/
│
├── api/
│ ├── currency_api.py
│ └── api_key.py
│
├── core/
│ ├── analytics.py
│ ├── database.py
│ └── models.py
│
├── tabs/
│ ├── dashboard.py
│ ├── transactions.py
│ └── settings.py
│
├── app.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Getting Started

### 1. Install Dependencies
```commandline
pip install -r requirements.txt
```
### 2. Insert API key
Go to `api/api_key.py` and insert the `EXCHANGE_API_KEY` value with the given API key from Exchange Rate Host.

### 3. Run the app
```commandline
streamlit run app.py
```
### 4. Visit the app
* The browser will automatically open along with the app.
* If the browser does not open, go to the url: http://localhost:8501

## How Currency Conversion Works

- Base currency is stored in a settings table  
- All amounts are converted automatically using `convert_to_base()`  
- The conversion function uses live API rates with minimal API usage  
- Cached once per session to avoid unnecessary calls  

## Adding New Currencies

Simply edit the global list in `currency_api.py`:

```
CURRENCY_LIST = ["USD", "MMK", "EUR", "JPY", "SGD", "THB", "CNY", Add Here]
```

No other changes required.

## Notes

- Streamlit reruns the script on UI updates.  
- Success and error messages persist using `st.session_state["message"]`.  
- Write operations (`add`, `delete`, `update`) auto-refresh via `st.rerun()`.

## Author
Htet Aung Hlaing

## Version History
- 1.0 

## Acknowledgments
- [Streamlit Documentation](9https://docs.streamlit.io/)
- [Plotly Express](https://plotly.com/python/plotly-express/)
- [SQLite](https://www.sqlite.org/)
- [Exchange Host API](https://exchangerate.host/)