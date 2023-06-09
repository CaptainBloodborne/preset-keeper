import asyncio

from datetime import datetime, timedelta

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response

from utils import USER_KEY, create_storage, get_page, apply_filters, Application

routes = web.RouteTableDef()


async def clear_tasks(app: Application):
    while True:
        for token, value in app[USER_KEY].items():
            print(f"Checking {token} ...")
            last_update = value.get("last_update")
            print("Last update time is", last_update)
            if last_update  - datetime.now() >= timedelta(hours=1, minutes=30):
                app[USER_KEY][token] = dict()
        await asyncio.sleep(1800)


async def background_tasks(app: Application):
    app['clear_task'] = asyncio.create_task(clear_tasks(app))

    yield

    await app['clear_task']


@routes.get("/get_products/")
async def get_products(request: Request) -> Response:
    return web.json_response(
        {
            "products": [request.app[USER_KEY][token].get("presets") for token in request.app[USER_KEY]]
        }
    )


@routes.post("/get_products/{token}/{preset_id}")
async def get_products(request: Request) -> Response:
    token: str = request.match_info["token"]
    preset_id: int = int(request.match_info["preset_id"])
    if not request.can_read_body:
        raise web.HTTPBadRequest

    body = await request.json()
    page: int = body.get("page", 1)
    offset: int = body.get("offset", 100)
    filters: dict = body.get("filters", None)
    debug: bool = body.get("debug")

    products_keeper: dict = request.app[USER_KEY].get(token)
    if products_keeper is None:
        raise web.HTTPNotFound

    preset = products_keeper["presets"].get(preset_id, {})
    preset_info = preset.get("preset_info", {})
    preset = preset.get("products", [])
    if filters:
        preset = list(
            filter(lambda product: apply_filters(product, filters), preset)
        )
    if debug:
        return web.json_response(
            {
                "products": get_page(products=preset, page=page, offset=offset),
                "total": len(preset),
                "preset_info": preset_info,
            }
        )

    return web.json_response(
        {
            "products": get_page(products=preset, page=page, offset=offset),
            "total": len(preset),
            "products_ids": preset_info.get("products_ids"),
        }
    )


@routes.post("/add_products")
async def add_products(request: Request) -> Response:
    if not request.can_read_body:
        raise web.HTTPBadRequest

    body = await request.json()

    token = body.get("token")
    preset_keeper = request.app[USER_KEY]
    if token not in preset_keeper:
        preset_keeper[token] = {
            "presets": dict(),
            "last_update": datetime.now(),
        }

    preset_id: int = body.get("preset_id")
    preset_keeper[token]["presets"][preset_id] = {}

    preset: dict = body.get("preset")
    preset_info: dict = body.get("preset_info")

    preset_keeper[token]["presets"][preset_id]["products"] = preset
    preset_keeper[token]["presets"][preset_id]["preset_info"] = preset_info

    return web.Response(status=201)


app = web.Application(client_max_size=1024 ** 3)
app.on_startup.append(create_storage)
app.cleanup_ctx.append(background_tasks)


app.add_routes(routes)
web.run_app(app, port=9090)
