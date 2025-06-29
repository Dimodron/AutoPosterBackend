from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from dependencies import authorize
from database     import database

from httpx  import AsyncClient
from typing import Any
from os     import environ


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ['*'], # ON PRODUCTION SET TO 'https://app.auto-poster.online'
    allow_credentials = True,
    allow_methods     = ['*'],
    allow_headers     = ['*'],
    expose_headers    = ['*']
)

services: dict[str, str] = {
    'scheduler' : environ.get('SERVICE_SCHEDULER_URL'),
    'payments'  : environ.get('SERVICE_PAYMENTS_URL'),
    # 'social'    : environ.get('SERVICE_SOCIAL_URL')
}

async def forward(service_url: str, method: str, path: str, body = None, headers = None):
    async with AsyncClient() as client:
        url: str = f'{service_url}{path}'
        
        response = await client.request(method, url, data = body, headers = headers)

        return response

@app.post('/login')
async def login(email: str, password: str):
    response = database.auth.sign_in_with_password({ 'email' : email, 'password' : password })

    return {
        'access_token' : response.session.access_token
    }    

@app.post('/payments/webhook/yoomoney/confirm_payment')
async def yoomoney_webhook(request: Request) -> Response:
    body = await request.body()
    
    headers = dict(request.headers)
    
    resp = await forward(
        services['payments'],
        request.method,
        '/webhook/yoomoney/confirm_payment',
        body,
        headers
    )
    
    return Response(
        content     = resp.content,
        status_code = resp.status_code,
        headers     = resp.headers,
        media_type  = resp.headers.get('content-type')
    )

@app.api_route(
    '/{service}/{path:path}', 
    dependencies = [Depends(authorize)],
    
    summary = 'Gateway route for accessing internal services',

    methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
)
async def gateway(service: str, path: str, request: Request, user: dict = Depends(authorize)) -> Response:
    if service not in services:
        raise HTTPException(
            status_code = 404,
            detail      = 'Unknown service'
        )
    
    service_url: str            = services.get(service)
    headers: dict[str, str]     = dict(request.headers)
    body: dict[str, Any] | None = await request.body()
    
    response = await forward(
        service_url, 
        request.method, 
        f'/{path}', 
        body, 
        {
            'User' : user.id,
            **headers
        }
    )

    return Response(
        content     = response.content,
        status_code = response.status_code,
        headers     = response.headers,
        media_type  = response.headers.get('content-type')
    )

