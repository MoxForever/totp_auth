from fastapi import APIRouter

from . import root, servers, users, widgets

router = APIRouter()
router.include_router(root.router)
router.include_router(servers.router)
router.include_router(users.router)
router.include_router(widgets.router)
