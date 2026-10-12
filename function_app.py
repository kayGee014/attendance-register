import azure.functions as func
from app import create_app

flask_app = create_app()
app = func.WsgiFunctionApp(app=flask_app.wsgi_app, http_auth_level=func.AuthLevel.ANONYMOUS)
