import os
import psycopg2
from faker import Faker

def create_table_and_fill_data():
    connection = None
    try:
        connection = psycopg2.connect(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host="postgres",
            port="5432",
            database="test"
        )
        cursor = connection.cursor()

        cursor.execute("DROP TABLE IF EXISTS test_data;")

        cursor.execute("""
            CREATE TABLE test_data (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                email VARCHAR(100)
            );
        """)

        fake = Faker()
        for _ in range(10000):
            cursor.execute("INSERT INTO test_data (name, email) VALUES (%s, %s)", (fake.name(), fake.email()))

        connection.commit()
        print("Таблица успешно создана и заполнена данными.")
        
    except Exception as error:
        print(f"Ошибка: {error}")
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_table_and_fill_data()
