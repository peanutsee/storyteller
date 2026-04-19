class DBClient:
    def __init__(self, path_to_db: str = "src/core/database"):
        self.path_to_db = path_to_db
        self.connection = None

    def create_tables(self):
        # 0. Connect to DB
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