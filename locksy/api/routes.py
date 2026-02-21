# This module defines the API routes for the Locksy application using FastAPI. 
# It includes endpoints for user registration, adding new encrypted items, retrieving existing items, and listing all items

from __future__ import annotations

import base64
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from locksy.api.settings import settings
from locksy.services.auth import register, unlock_dek
from locksy.services.locker import add_evidence, get_evidence, list_evidence

router = APIRouter()

DATABASE_PATH = settings.db_path

# Pydantic models for request bodies for the API endpoints, 
# including user registration, authentication, adding items, and retrieving items.

class RegisterReq(BaseModel):
    username: str
    password: str

class AuthReq(BaseModel):
    username: str
    password: str

class AddReq(AuthReq):
    name: str
    data_b64: str  # base64 encoded evidence bytes

class GetReq(AuthReq):
    item_id: int

# API endpoint to register a new user, which calls the register function from the auth service and returns the new user's ID.
@router.post("/register")
def register_user(req: RegisterReq):
    try:
        user_id = register(DATABASE_PATH, req.username, req.password)
        return {"user_id": user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# API endpoint to add a new encrypted item (evidence) for a user, 
# which authenticates the user and calls the add_evidence function from the locker service, 
# returning the new item's ID.
@router.post("/add")
def add_item(req: AddReq):
    try:
        user_id, dek = unlock_dek(DATABASE_PATH, req.username, req.password)
        data = base64.b64decode(req.data_b64)
        item_id = add_evidence(DATABASE_PATH, user_id, dek, req.name, data)
        return {"item_id": item_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# API endpoint to retrieve an existing encrypted item (evidence) by its ID, 
# which authenticates the user and calls the get_evidence function from the locker service, 
# returning the item's name and base64-encoded plaintext data.
@router.post("/get")
def get_item(req: GetReq):
    try:
        user_id, dek = unlock_dek(DATABASE_PATH, req.username, req.password)
        name, data = get_evidence(DATABASE_PATH, user_id, dek, req.item_id)
        return {"name": name, "data_b64": base64.b64encode(data).decode("utf-8")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# API endpoint to list all encrypted items (evidence) associated with a user, 
# which authenticates the user and calls the list_evidence function from the locker service, 
# returning a list of items with their ID, name, creation timestamp, and size in bytes.
@router.post("/list")
def list_items(req: AuthReq):
    try:
        user_id, _dek = unlock_dek(DATABASE_PATH, req.username, req.password)
        rows = list_evidence(DATABASE_PATH, user_id)
        return {"items": [{"id": r[0], "name": r[1], "created_at": r[2], "size_bytes": r[3]} for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))