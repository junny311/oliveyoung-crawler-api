# database.py
import psycopg2
from db_config import DB_CONFIG # 방금 만든 설정 파일 임포트

def get_db_connection():
    """ PostgreSQL 데이터베이스 커넥션을 생성합니다. """
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )
        print("Database connection successful!")
        return conn
    except psycopg2.Error as error:
        print(f"Error while connecting to PostgreSQL: {error}")
        return None
    except Exception as error:
        print(f"An unexpected error occurred: {error}")
        return None

def create_table(conn):
    """ 'products' 테이블을 생성합니다. 이미 존재하면 생성하지 않습니다. """
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    product_id VARCHAR(255) PRIMARY KEY,
                    brand_name VARCHAR(255),
                    product_name VARCHAR(255),
                    original_price INT,
                    sale_price INT,
                    rating_score FLOAT,
                    review_count INT,
                    crawled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("Table 'products' created or already exists.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error creating table: {error}")
        conn.rollback()

def insert_products(conn, products):
    """ 상품 데이터를 데이터베이스에 삽입 또는 업데이트합니다. """
    if not products:
        return
        
    sql = """
        INSERT INTO products (product_id, brand_name, product_name, original_price, sale_price, rating_score, review_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_id) DO UPDATE SET
            brand_name = EXCLUDED.brand_name,
            product_name = EXCLUDED.product_name,
            original_price = EXCLUDED.original_price,
            sale_price = EXCLUDED.sale_price,
            rating_score = EXCLUDED.rating_score,
            review_count = EXCLUDED.review_count,
            crawled_at = CURRENT_TIMESTAMP;
    """
    
    try:
        with conn.cursor() as cur:
            # executemany를 사용하여 여러 데이터를 한 번에 처리
            data_to_insert = [
                (
                    p['product_id'], p['brand_name'], p['product_name'],
                    p['original_price'], p['sale_price'], p['rating_score'], p['review_count']
                )
                for p in products
            ]
            cur.executemany(sql, data_to_insert)
        conn.commit()
        print(f"Successfully inserted/updated {len(products)} products.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error inserting products: {error}")
        conn.rollback()


if __name__ == '__main__':
    # 모듈 테스트용 코드
    conn = get_db_connection()
    if conn:
        create_table(conn)
        # 테스트용 데이터
        test_products = [
            {
                'product_id': 'A000000123456', 'brand_name': 'Test Brand', 'product_name': 'Test Product',
                'original_price': 10000, 'sale_price': 8000, 'rating_score': 4.5, 'review_count': 100
            }
        ]
        insert_products(conn, test_products)
        conn.close()
        print("Database connection closed.")