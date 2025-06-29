from fastapi import Header, HTTPException
from database import database

async def authorize(
    access_token: str = Header(..., alias = 'Authorization', description = 'Supabase access_token of user')
):    
    try:
        if not access_token:
            raise HTTPException(
                status_code = 401, 
                detail      = 'Unauthorized'
            )
        
        user = database.auth.get_user(access_token)

        return user.user

    except Exception:
        raise HTTPException(
            status_code = 401, 
            detail      = 'Unauthorized'
        )