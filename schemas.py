from datetime import datetime
from pydantic import BaseModel, ConfigDict

class Product(BaseModel):
    """올리브영 상품 정보를 표현하는 Pydantic 모델"""
    
    # Model Config
    model_config = ConfigDict(from_attributes=True)
    
    # Fields
    product_id: str
    brand_name: str
    product_name: str
    original_price: int
    sale_price: int
    rating_score: float
    review_count: int
    crawled_at: datetime