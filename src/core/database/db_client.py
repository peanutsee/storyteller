import sqlite3
import os
import uuid
import random
from datetime import datetime


class DBClient:
    def __init__(
        self, path_to_db: str = "src/core/database", db_name: str = "storyteller.db"
    ):
        self.path_to_db = path_to_db
        self.db_name = db_name
        self.full_path = os.path.join(self.path_to_db, self.db_name)
        self.connection = None

    def connect(self):
        """Establishes the database connection."""
        os.makedirs(self.path_to_db, exist_ok=True)
        self.connection = sqlite3.connect(self.full_path)

        self.connection.row_factory = sqlite3.Row
        return self.connection

    def disconnect(self):
        """Safely closes the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    # Enable Context Manager (the 'with' statement)
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def create_tables(self):
        """Creates the necessary schema."""
        if not self.connection:
            raise ConnectionError("Database is not connected. Call connect() first.")

        cursor = self.connection.cursor()

        # 1. Create Portfolio Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id TEXT PRIMARY KEY,
                owner TEXT,
                total_amount REAL,
                last_updated DATETIME
            )
        """)

        # 2. Create Exposure Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS exposure (
                id TEXT PRIMARY KEY,
                portfolio_id TEXT,
                ticker_symbol TEXT,
                quantity REAL,
                avg_price REAL,
                FOREIGN KEY (portfolio_id) REFERENCES portfolio(id)
            )
        """)

        self.connection.commit()

    def has_data(self) -> bool:
        """Checks if there is already data in the database."""
        if not self.connection:
            raise ConnectionError("Database is not connected. Call connect() first.")
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM portfolio")
            count = cursor.fetchone()[0]
            return count > 0
        except sqlite3.OperationalError:
            return False

    def _add_portfolio(self, owner: str, total_amount: float) -> str:
        """Inserts a new portfolio and returns its UUID."""
        cursor = self.connection.cursor()
        portfolio_id = str(uuid.uuid4())

        cursor.execute(
            """
            INSERT INTO portfolio (id, owner, total_amount, last_updated)
            VALUES (?, ?, ?, ?)
        """,
            (portfolio_id, owner, total_amount, datetime.now()),
        )

        self.connection.commit()
        return portfolio_id

    def _add_exposure(
        self, portfolio_id: str, ticker: str, quantity: float, avg_price: float
    ) -> str:
        """Inserts a new exposure linked to a portfolio."""
        cursor = self.connection.cursor()
        exposure_id = str(uuid.uuid4())

        cursor.execute(
            """
            INSERT INTO exposure (id, portfolio_id, ticker_symbol, quantity, avg_price)
            VALUES (?, ?, ?, ?, ?)
        """,
            (exposure_id, portfolio_id, ticker, quantity, avg_price),
        )

        self.connection.commit()
        return exposure_id

    def seed_mock_data(self):
        """Seeds the database with 10 mock portfolios and 5 exposures each from S&P 500."""
        sp500_tickers = [
            "AAPL",
            "MSFT",
            "AMZN",
            "NVDA",
            "GOOGL",
            "META",
            "BRK.B",
            "TSLA",
            "UNH",
            "JNJ",
            "JPM",
            "V",
            "PG",
            "MA",
            "HD",
            "CVX",
            "MRK",
            "ABBV",
            "PEP",
            "KO",
            "WMT",
            "COST",
            "MCD",
            "CSCO",
            "CRM",
            "PFE",
            "TMO",
            "ABT",
            "DHR",
            "NFLX",
            "ADBE",
            "AMD",
            "CMCSA",
            "DIS",
            "BA",
            "INTC",
            "TXN",
            "PM",
            "COP",
            "HON",
        ]

        owners = [f"Mock Owner {i + 1}" for i in range(10)]

        for owner in owners:
            exposures_data = []
            total_amount = 0.0

            selected_tickers = random.sample(sp500_tickers, 5)

            for ticker in selected_tickers:
                avg_price = round(random.uniform(50.0, 500.0), 2)
                quantity = round(random.uniform(1.0, 100.0), 2)
                total_amount += avg_price * quantity
                exposures_data.append((ticker, quantity, avg_price))

            portfolio_id = self._add_portfolio(owner, round(total_amount, 2))

            for ticker, quantity, avg_price in exposures_data:
                self._add_exposure(portfolio_id, ticker, quantity, avg_price)
