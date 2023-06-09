from aiohttp.web_app import Application


USER_KEY = "user"


async def create_storage(app: Application) -> bool:
    app[USER_KEY] = dict()
    return True


def apply_filters(product: dict, filters: dict):
    return all([product.get(filter_name) in filters.get(filter_name) for filter_name in filters])



def get_page(products: list[dict], page: int = 1, offset: int = 100):
    total_pages = len(products) // offset

    if page == total_pages:
        return products[offset * (page - 1): len(products)]

    return products[offset * (page - 1): offset * page]