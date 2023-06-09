from attrs import define


@define
class ProductDetails:
    nm_id: int
    seller_id: int
    sold_amount: float
    timestamp: int
    subject_id: int
    brand_id: int
    price: int
    stock_exists: bool


@define
class AddFilters:
    season_id: int
    kind_id: int
    color_ids: list[int]


@define
class Product:
    product_details: ProductDetails
    add_filters: AddFilters
    Score: float
    primal_score: float
    score_ksort: float


@define
class Preset:
    products: list[Product]
    total_products: int
    subjects: list[int]
    brands: list[int]
