from datetime import datetime

from aiohttp import ClientSession
from asyncpg import create_pool
from fastapi import Header, HTTPException, Query, status
from jose import jwt

from config.common import config


def auth_dep(authorization: str = Header(...)):
    if authorization != config.authorization:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)


async def aiohttp_session():
    session = ClientSession(headers={"Accept": "application/json"})
    try:
        yield session
    finally:
        await session.close()


def state_check(state: str = Query(...)) -> int:
    try:
        payload = jwt.decode(state, config.secret)
    except jwt.JWTError:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, "Invalid state")

    expiry = datetime.fromisoformat(payload['expiry'])
    if datetime.now() > expiry:
        raise HTTPException(status.HTTP_406_NOT_ACCEPTABLE, "Too late")

    return payload['id']


db_pool = create_pool(config.database_uri)


def db_connection():
    return db_pool