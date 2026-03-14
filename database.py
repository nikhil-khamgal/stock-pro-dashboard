import sqlite3
import hashlib

# =========================
# DATABASE CONNECTION
# =========================

conn = sqlite3.connect("portfolio.db", check_same_thread=False)
cursor = conn.cursor()

# =========================
# TABLES
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS portfolio(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    stock_symbol TEXT,
    investment REAL,
    buy_price REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

# =========================
# PASSWORD HASH
# =========================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================
# SIGNUP
# =========================

def signup(username, password):

    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (username, hash_password(password))
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False


# =========================
# LOGIN
# =========================

def login(username, password):

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    user = cursor.fetchone()

    return user is not None


# =========================
# ADD STOCK
# =========================

def add_stock(username, stock_symbol, investment, buy_price):

    cursor.execute(
        """INSERT INTO portfolio(username,stock_symbol,investment,buy_price)
           VALUES (?,?,?,?)""",
        (username, stock_symbol, investment, buy_price)
    )

    conn.commit()


# =========================
# GET PORTFOLIO
# =========================

def get_portfolio(username):

    cursor.execute(
        """SELECT id, stock_symbol, investment, buy_price
           FROM portfolio
           WHERE username=?""",
        (username,)
    )

    return cursor.fetchall()


# =========================
# DELETE STOCK
# =========================

def delete_stock(stock_id):

    cursor.execute(
        "DELETE FROM portfolio WHERE id=?",
        (stock_id,)
    )

    conn.commit()


# =========================
# CLEAR USER PORTFOLIO
# =========================

def clear_portfolio(username):

    cursor.execute(
        "DELETE FROM portfolio WHERE username=?",
        (username,)
    )

    conn.commit()