from fastapi import FastAPI, HTTPException
from typing import List
import psycopg2.extras
from psycopg2.extras import RealDictCursor

# Product 스키마와 DB 연결 함수를 임포트
from schemas import Product
from database import get_db_connection

# --- FastAPI 앱 초기화 ---
app = FastAPI(
    title="올리브영 상품 데이터 API",
    description="크롤링으로 수집된 올리브영 상품 데이터를 제공하는 API입니다.",
    version="1.0.0"
)

# --- API 엔드포인트 정의 ---
@app.get(
    "/products",
    response_model=List[Product],
    summary="모든 상품 데이터 조회",
    description="데이터베이스에 저장된 모든 상품 정보를 JSON 형태로 반환합니다."
)
def get_products():
    """
    모든 상품 정보를 조회합니다.
    
    Returns:
        List[Product]: 상품 정보 리스트
    """
    conn = None
    try:
        # DB 연결 (RealDictCursor 사용)
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # 전체 상품 조회
        cur.execute("SELECT * FROM products")
        products = cur.fetchall()
        
        # 커서 닫기
        cur.close()
        
        if not products:
            # 데이터가 없으면 빈 리스트 반환
            return []
        
        # RealDictCursor로 가져온 딕셔너리를 Product 모델로 변환
        return [Product(**product) for product in products]

    except HTTPException as http_exc:
        # HTTPException은 그대로 다시 발생시킵니다.
        raise http_exc
    except Exception as e:
        # 그 외 다른 예외가 발생했을 경우, 500 서버 에러를 반환합니다.
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"서버 내부 오류가 발생했습니다: {e}")
    finally:
        # 데이터베이스 커넥션을 항상 닫아줍니다.
        if conn:
            conn.close()

@app.get("/")
def read_root():
    return {"message": "올리브영 데이터 파이프라인 API에 오신 것을 환영합니다. /docs 로 이동하여 API 문서를 확인하세요."}