from aiohttp.web_app import Application

from app.admin.routes import setup_routes as admin_setup_routes

__all__ = ("setup_routes",)


def setup_routes(application: Application):
    admin_setup_routes(application)
