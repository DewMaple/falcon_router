from ..router import route

@route("/hello", method="GET")
def hello(org_id: int):
    return "Hello"