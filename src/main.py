"""_summary_

contains all routes

Returns:
    _type_: _description_
"""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def index():
    """_summary_

    default hello world route

    Returns:
        _type_: _description_
    """
    return {"details": "Hello, World!"}
