from app import app

from os import environ
import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        app, 
        host = '0.0.0.0', 
        port = int(environ.get('PORT', 5555))
    )
