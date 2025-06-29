from gateway import app
from os import environ

import uvicorn

if __name__ == '__main__':  
    uvicorn.run(
        app,
        host   = environ.get('HOST', '127.0.0.1'),
        port   = int(environ.get('PORT', 8000))
    )
