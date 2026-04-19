from src.core.database.db_client import DBClient


def main():
    # 0. Create DBClient
    db_client = DBClient()
    db_client.connect()
    db_client.create_tables()

    if not db_client.has_data():
        print("Database is empty. Seeding mock data...")
        db_client.seed_mock_data()
    else:
        print("Database already contains data. Skipping mock data seeding.")

if __name__ == "__main__":
    main()
