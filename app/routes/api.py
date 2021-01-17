from fastapi import APIRouter

from app.routes import shop_skin, teapot

router = APIRouter()
router.include_router(shop_skin.router)
router.include_router(teapot.router)