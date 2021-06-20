import falcon
from ..router import register_routes

app: Optional[falcon.API] = None

def create_app():
    global app
    app = falcon.API()
    register_routes(app)
    return app