import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objs as go
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from streamlit_autorefresh import st_autorefresh

from database import signup, login, add_stock, get_portfolio,delete_stock

#css func
def load_css():

    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)



# ====================================
# PAGE CONFIG
# ====================================

st.set_page_config(
    page_title="Stock Pro Dashboard",
    layout="wide",
    page_icon="📈"
)


# ====================================
# CONSTANT DATA
# ====================================

STOCKS = {
    "Amazon": "AMZN",
    "Apple": "AAPL",
    "Google": "GOOGL",
    "Meta": "META",
    "Microsoft": "MSFT",
    "Netflix": "NFLX",
    "Nvidia": "NVDA"
}

TUTORIALS = [
    {"title": "Getting Started with Stock Investing", "content": "Start by understanding your financial goals and risk tolerance. Open a brokerage account, research companies, and start with small investments. Diversify your portfolio across different sectors.", "level": "Beginner"},
    {"title": "Understanding Stock Charts", "content": "Learn to read candlestick charts, volume indicators, and moving averages. Charts help identify trends, support/resistance levels, and potential entry/exit points.", "level": "Beginner"},
    {"title": "Fundamental vs Technical Analysis", "content": "Fundamental analysis examines company financials, earnings, and industry position. Technical analysis uses charts and patterns to predict price movements. Use both for informed decisions.", "level": "Intermediate"},
    {"title": "Risk Management Strategies", "content": "Never invest more than you can afford to lose. Use stop-loss orders, diversify investments, and maintain a balanced portfolio. The 1% rule: don't risk more than 1% of capital on a single trade.", "level": "Intermediate"},
    {"title": "Advanced Trading Strategies", "content": "Learn about options trading, swing trading, and momentum strategies. Understand market indicators, use technical analysis tools, and develop a disciplined trading plan.", "level": "Advanced"},
    {"title": "Building a Long-Term Portfolio", "content": "Focus on quality companies with strong fundamentals. Use dollar-cost averaging, reinvest dividends, and think long-term. Rebalance portfolio annually to maintain target allocations.", "level": "Beginner"}
]

GLOSSARY = {
    "Bull Market": "A market condition where prices are rising or expected to rise.",
    "Bear Market": "A market condition where prices are falling by 20% or more.",
    "Market Cap": "Market Capitalization - total value of a company's outstanding shares.",
    "P/E Ratio": "Price-to-Earnings ratio - measures stock price relative to earnings per share.",
    "Volatility": "The degree of variation in stock prices over time.",
    "Dividend": "A portion of company profits distributed to shareholders.",
    "IPO": "Initial Public Offering - when a company first sells shares to the public.",
    "Blue Chip": "Stock of a large, well-established, financially stable company.",
    "Candlestick": "A chart showing open, high, low, and close prices for a period.",
    "Moving Average": "Average stock price over a specific time period to smooth out fluctuations.",
    "RSI": "Relative Strength Index - momentum indicator measuring speed and change of price movements.",
    "MACD": "Moving Average Convergence Divergence - trend-following momentum indicator.",
    "Support Level": "Price level where stock tends to stop falling and bounce back.",
    "Resistance Level": "Price level where stock tends to stop rising.",
    "Day Trading": "Buying and selling stocks within the same trading day.",
    "Long Position": "Buying stock with expectation that price will increase.",
    "Short Position": "Selling borrowed stock expecting to buy it back at lower price.",
    "ETF": "Exchange-Traded Fund - investment fund traded on stock exchanges.",
    "Index": "Measure of stock market performance (e.g., S&P 500, NASDAQ).",
    "Correlation": "Statistical measure of how two stocks move in relation to each other."
}


# ====================================
# DATA FUNCTIONS
# ====================================

@st.cache_data
def fetch_live_stock_data(symbol):

    stock = yf.Ticker(symbol)

    df = stock.history(period="1y")

    df.reset_index(inplace=True)

    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)

    return df


@st.cache_data
def get_live_price(symbol):
    

    stock = yf.Ticker(symbol)

    hist = stock.history(period="1d")

    if hist.empty:
        return None

    return hist["Close"].iloc[-1]

# ====================================
# TOP GAINERS / LOSERS
# ====================================
def top_movers():

    stocks = ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","NFLX"]

    gainers = []
    losers = []

    for s in stocks:

        try:
            stock = yf.Ticker(s)
            df = stock.history(period="2d")

            if len(df) < 2:
                continue

            prev = df["Close"].iloc[-2]
            current = df["Close"].iloc[-1]

            change = ((current - prev) / prev) * 100

            if change > 0:
                gainers.append((s, change))
            else:
                losers.append((s, change))

        except:
            pass

    gainers = sorted(gainers, key=lambda x: x[1], reverse=True)[:3]
    losers = sorted(losers, key=lambda x: x[1])[:3]

    col1, col2 = st.columns(2)

    with col1:

        html = """
        <div class="market-card">
        <div class="card-title">🔥 Top Gainers</div>
        """

        for g in gainers:
            html += f'<div class="gainer">{g[0]}  +{g[1]:.2f}%</div>'

        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)

    with col2:

        html = """
        <div class="market-card">
        <div class="card-title">📉 Top Losers</div>
        """

        for l in losers:
            html += f'<div class="loser">{l[0]}  {l[1]:.2f}%</div>'

        html += "</div>"

        st.markdown(html, unsafe_allow_html=True)
# ====================================
# MARKET HEATMAP
# ====================================
def market_heatmap():

    stocks = ["AAPL","MSFT","NVDA","AMZN","GOOGL","META","NFLX"]

    data = []

    for s in stocks:

        try:
            stock = yf.Ticker(s)

            df = stock.history(period="2d")

            prev = df["Close"].iloc[-2]
            current = df["Close"].iloc[-1]

            change = ((current-prev)/prev)*100

            data.append({"Stock":s,"Change":change})

        except:
            pass

    df_heat = pd.DataFrame(data)

    fig = px.treemap(
        df_heat,
        path=["Stock"],
        values="Change",
        color="Change",
        color_continuous_scale="RdYlGn"
    )

    fig.update_layout(height=400)

    st.markdown('<div class="heatmap-box">', unsafe_allow_html=True)

    st.subheader("🔥 Market Heatmap")

    st.plotly_chart(fig,use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
# ====================================
# LIVE STOCK TICKER
# ====================================

def live_ticker():

    symbols = ["AAPL","MSFT","NVDA","AMZN","GOOGL"]

    ticker_text = ""

    for s in symbols:

        try:
            price = get_live_price(s)
            ticker_text += f"{s}: ${price:.2f} | "
        except:
            ticker_text += f"{s}: N/A | "

    ticker_html = f"""
    <div class="ticker-container">
        <div class="ticker">
            📈 Live Market: {ticker_text}
        </div>
    </div>
    """

    st.markdown(ticker_html, unsafe_allow_html=True)  



# ====================================
# INDICATORS
# ====================================

def add_indicators(df):
    market_heatmap()

    df["MA10"] = df["Close"].rolling(10).mean()

    delta = df["Close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    exp1 = df["Close"].ewm(span=12, adjust=False).mean()
    exp2 = df["Close"].ewm(span=26, adjust=False).mean()

    df["MACD"] = exp1 - exp2
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()

    return df


# ====================================
# ML MODEL
# ====================================

def get_prediction_models(df):

    df["Day"] = np.arange(len(df))

    X = df[["Day"]]
    Y = df["Close"]

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor()
    }

    for model in models.values():
        model.fit(X, Y)

    return models, X, Y


# ====================================
# LOGIN PAGE
# ====================================

def login_page():

    

    st.markdown(
        """
        <div class="login-box">
        <div class="title">📈 Stock Pro</div>
        <div class="subtitle">AI Powered Stock Dashboard</div>
        """,
        unsafe_allow_html=True
    )

    menu = st.radio("Select", ["Login", "Signup"], horizontal=True)

    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    if menu == "Signup":

        if st.button("Create Account 🚀"):

            if signup(username, password):
                st.success("Account created successfully")
            else:
                st.error("User already exists")

    if menu == "Login":

        if st.button("Login 🔐"):

            if login(username, password):

                st.session_state.user = username
                st.rerun()

            else:
                st.error("Invalid username or password")

    st.markdown("</div>", unsafe_allow_html=True)

# ====================================
# DASHBOARD
# ====================================

def dashboard():
    live_ticker() 
    top_movers()
    
    st_autorefresh(interval=60000, key="refresh")

    st.sidebar.markdown(
    '<div class="sidebar-title">📊 Stock Pro</div>',
    unsafe_allow_html=True
)

    st.sidebar.success(f"User: {st.session_state.user}")

    if st.sidebar.button("Logout"):

        st.session_state.user = None
        st.rerun()

    # SEARCH STOCK

    st.sidebar.subheader("🔎 Search Any Stock")

    search_symbol = st.sidebar.text_input(
        "Enter Stock Ticker (AAPL, TSLA, RELIANCE.NS)"
    )

    st.sidebar.markdown("OR")

    default_stock = st.sidebar.selectbox(
        "Choose Popular Stock",
        list(STOCKS.keys())
    )

    if search_symbol:
        symbol = search_symbol.upper()
    else:
        symbol = STOCKS[default_stock]

    # LOAD DATA

    try:

        df = fetch_live_stock_data(symbol)

        if df.empty:
            st.error("Invalid stock symbol")
            return

        df = add_indicators(df)

        price = get_live_price(symbol)

    except:

        st.error("Stock data not available")
        return
    

    

    # TOP METRICS

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Live Price", f"${price:.2f}")
    col2.metric("52W High", f"${df['High'].max():.2f}")
    col3.metric("52W Low", f"${df['Low'].min():.2f}")
    col4.metric("Avg Volume", f"{int(df['Volume'].mean()):,}")

    st.divider()

    # CANDLE CHART

    st.subheader(f"📈 {symbol} Chart")

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df["Date"],
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"]
    ))

    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["MA10"],
        name="MA10"
    ))

    fig.update_layout(template="plotly_dark", height=600)

    st.plotly_chart(fig, use_container_width=True)

    # AI PREDICTION

    st.subheader("🤖 AI Prediction")

    models, X, Y = get_prediction_models(df)

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(x=df["Date"], y=Y, name="Actual"))

    fig2.add_trace(go.Scatter(
        x=df["Date"],
        y=models["Linear Regression"].predict(X),
        name="Prediction"
    ))

    fig2.update_layout(template="plotly_dark")

    st.plotly_chart(fig2, use_container_width=True)

    # RSI

    st.subheader("RSI Indicator")

    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=df["Date"],
        y=df["RSI"],
        name="RSI"
    ))

    fig3.add_hline(y=70)
    fig3.add_hline(y=30)

    fig3.update_layout(template="plotly_dark")

    st.plotly_chart(fig3, use_container_width=True)

    # PORTFOLIO

       # ====================================
    # PORTFOLIO
    # ====================================

    # ====================================
# PORTFOLIO
# ====================================

    st.subheader("💼 Portfolio")

    investment = st.number_input("Investment", min_value=100, value=1000)

# ADD STOCK
    if st.button("Add Stock"):

         buy_price = get_live_price(symbol)

         if buy_price is None:
              st.error("Price not available")

         else:
            add_stock(
               st.session_state.user,
               symbol,
               investment,
               buy_price
             )

            st.success("Added to portfolio")


# LOAD PORTFOLIO DATA
    data = get_portfolio(st.session_state.user)

    if data:

         df_port = pd.DataFrame(
            data,
            columns=["ID", "Stock", "Investment", "Buy Price"]
         )

         current_prices = []
         current_values = []
         profits = []
         returns = []

    # CALCULATE PORTFOLIO VALUES
         for index, row in df_port.iterrows():

            stock = row["Stock"]
            invest = row["Investment"]
            buy_price = row["Buy Price"]

            price = get_live_price(stock)

            if price is None:
                 price = 0

            shares = invest / buy_price if buy_price != 0 else 0
            current_value = shares * price

            profit = current_value - invest
            percent = (profit / invest) * 100 if invest != 0 else 0

            current_prices.append(round(price, 2))
            current_values.append(round(current_value, 2))
            profits.append(round(profit, 2))
            returns.append(round(percent, 2))

    # ADD NEW COLUMNS
         df_port["Current Price"] = current_prices
         df_port["Current Value"] = current_values
         df_port["Profit / Loss"] = profits
         df_port["Return %"] = returns

    # DISPLAY TABLE
         st.subheader("Portfolio Table")

# Table Header
         h1, h2, h3, h4, h5, h6, h7 = st.columns(7)

         h1.write("Stock")
         h2.write("Investment")
         h3.write("Buy Price")
         h4.write("Current Price")
         h5.write("Current Value")
         h6.write("Profit/Loss")
         h7.write("Action")

# Table Rows
         for index, row in df_port.iterrows():

             c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

             c1.write(row["Stock"])
             c2.write(row["Investment"])
             c3.write(round(row["Buy Price"],2))
             c4.write(row["Current Price"])
             c5.write(row["Current Value"])
             profit = row["Profit / Loss"]

             color = "green" if profit >= 0 else "red"

             c6.markdown(f"<span style='color:{color}'>{profit}</span>", unsafe_allow_html=True)

             if c7.button("❌", key=row["ID"]):


                delete_stock(row["ID"])

                st.success("Stock Deleted")

                st.rerun()
         

    # TOTALS
         total_invest = df_port["Investment"].sum()
         total_value = df_port["Current Value"].sum()

         total_profit = total_value - total_invest
         total_return = (total_profit / total_invest) * 100 if total_invest != 0 else 0

         c1, c2, c3 = st.columns(3)

         c1.metric("Total Investment", f"${total_invest:.2f}")
         c2.metric("Current Value", f"${total_value:.2f}")
         c3.metric("Total Profit/Loss", f"${total_profit:.2f}", f"{total_return:.2f}%")

    # PIE CHART
         fig = px.pie(
            df_port,
            names="Stock",
             values="Investment"
          )

         fig.update_layout(template="plotly_dark")

         st.plotly_chart(fig, use_container_width=True)

    else:
       st.info("No stocks in portfolio") 

    # INVESTMENT CALCULATOR

    st.header("💰 Investment Profit Calculator")

    invest_amount = st.number_input(
        "Investment Amount",
        min_value=100,
        max_value=100000,
        value=1000,
        step=100
    )

    invest_date = st.date_input(
        "Investment Date",
        value=df["Date"].min().date()
    )

    invest_date = pd.to_datetime(invest_date).tz_localize(None)

    filtered = df[df["Date"] >= invest_date]

    if filtered.empty:

        st.warning("No data available for selected date")

    else:

        buy_price = filtered.iloc[0]["Close"]

        current_price = df.iloc[-1]["Close"]

        shares = invest_amount / buy_price

        current_value = shares * current_price

        profit = current_value - invest_amount

        return_percent = (profit / invest_amount) * 100

        c1, c2, c3 = st.columns(3)

        c1.metric("Buy Price", f"${buy_price:.2f}")
        c2.metric("Current Price", f"${current_price:.2f}")
        c3.metric("Shares Bought", f"{shares:.2f}")

        c4, c5 = st.columns(2)

        c4.metric("Current Value", f"${current_value:.2f}")
        c5.metric("Profit / Loss", f"${profit:.2f}", f"{return_percent:.2f}%")

    # TUTORIALS

    st.header("Investment Tutorials")

    for t in TUTORIALS:

        with st.expander(t["title"]):
            st.write(t["content"])

    # GLOSSARY

    st.header("Glossary")

    for k, v in GLOSSARY.items():

        st.write(f"**{k}** : {v}")


# ====================================
# MAIN FUNCTION
# ====================================

def main():
    load_css()

    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        login_page()
    else:
        dashboard()


# ====================================
# APP START
# ====================================

if __name__ == "__main__":
    main()