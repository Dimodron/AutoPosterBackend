from fastapi                 import FastAPI, HTTPException, Body, Header
from fastapi.responses       import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib              import asynccontextmanager
from typing                  import AsyncGenerator, Dict
from uuid                    import UUID
from datetime                import timedelta

from core     import Yookassa
from database import Database
from schemas  import YooMoneyWebhookSchema, PaymentInitiationSchema


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    app.state.database = await Database.serve()

    try:
        yield
    finally:
        ...

app = FastAPI(lifespan = lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ['*'],
    allow_credentials = True,
    allow_methods     = ['*'],
    allow_headers     = ['*'],
)


@app.post(
    '/initiate-payment',

    tags    = ['Payments'],
    summary = 'Initiate a payment for a user'
)
async def initiate_payment_endpoint(
    payment_request: PaymentInitiationSchema,
    user_id: UUID | None = Header(..., alias = 'User')
):   
    tariff = await app.state.database.get_tariff_by_id(payment_request.tariff_id)
    
    if not tariff:
        raise HTTPException(
            status_code = 404, 
            detail      = 'Tariff not found'
        )

    payment_api: Yookassa = Yookassa()
    
    result = await payment_api.initiate_payment(
        user_id, 
        payment_request.tariff_id, 
        tariff.price, 
        tariff.currency
    )

    return JSONResponse(
        {
            **result
        },
        status_code = 201
    )

@app.get(
    '/subscriptions/valid',

    tags    = ['Subscriptions'],
    summary = 'Check if a user\'s subscription is valid'
)
async def is_subscription_valid_endpoint(user_id: UUID | None = Header(..., alias = 'User')):
    is_subscription_valid: bool = await app.state.database.is_subscription_valid(user_id)
    
    return JSONResponse(
        {
            'is_valid' : is_subscription_valid
        },
        status_code = 200
    )


@app.post(
    '/webhook/yoomoney/confirm_payment',

    tags           = ['Webhooks'],
    summary        = 'Handle YooMoney webhook notifications'
)
async def yoomoney_webhook(webhook_data: YooMoneyWebhookSchema):
    # try:
    payment_id = webhook_data.object.id
    metadata   = webhook_data.object.metadata
    
    payment_date  = webhook_data.object.created_at
    amount_kopeks = int(float(webhook_data.object.amount.value) * 100)
    
    tarrif = (
        await app.state.database
            .client
            .table('tariffs')
            .select('days_valid, service')
            .eq('id', int(metadata.get('tariff_id')))
            .maybe_single()
            .execute()
    )

    if not tarrif:
        raise HTTPException(
            status_code = 404,
            detail      = 'Tariff not found'
        )
    
    valid_until = payment_date + timedelta(days = tarrif.data.get('days_valid'))
    
    payment_data = {
        'user_id'     : str(metadata.get('user_id')),
        'tariff_id'   : int(metadata.get('tariff_id')),
        'status'      : webhook_data.object.status,
        'amount'      : amount_kopeks,
        'currency'    : webhook_data.object.amount.currency,
        'valid_until' : valid_until.isoformat(),
        'payed_at'    : webhook_data.object.captured_at.isoformat() if webhook_data.object.captured_at else payment_date.isoformat(),
        'balance'     : amount_kopeks if webhook_data.object.paid else 0,
        'payment_id'  : str(payment_id)
    }

    await app.state.database.update_payment_from_webhook(payment_data)
        
    await app.state.database.client.table(tarrif.data.get('service')).update({
        'active_until' : valid_until.isoformat()
    }).eq('user_id', metadata.get('user_id')).execute()

    return JSONResponse(
        {
            'status': 'success'
        },
        status_code = 200
    )
        
    # except (KeyError, ValueError) as error:
    #     raise HTTPException(
    #         status_code = 400, 
    #         detail      = str(error)
    #     )
    
    # except Exception as error:
    #     raise HTTPException(
    #         status_code = 500, 
    #         detail      = str(error)
    #     )


