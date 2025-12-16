from database import DatabaseManager
from config.db_config import DEFAULT_CONFIG


def main():
    db = DatabaseManager()
    success, message = db.connect(**DEFAULT_CONFIG)
    print(message)

    if success:
        ok, info = db.test_tables()
        if ok:
            print("Tables status:")
            for table, exists in info.items():
                print(f"- {table}: {exists}")
        db.close()


if __name__ == "__main__":
    main()
