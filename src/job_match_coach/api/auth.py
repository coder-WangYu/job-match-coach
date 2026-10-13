from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from job_match_coach.auth.supabase_client import get_supabase

router = APIRouter()

# 用户注册
class UserRegister(BaseModel):
    email: str
    password: str
    role: Literal["job_seeker", "head_hunter", "hr"]

@router.post("/register")
def register(body: UserRegister) -> dict:
    try:
        result = get_supabase().auth.sign_up({
            "email": body.email,
            "password": body.password,
            "options": {
                "data": {
                    "role": body.role
                }
            }
        })

        return {
            "user_id": result.user.id,
            "email": body.email,
            "role": body.role
        }
    except Exception as e:
        raise HTTPException(400, str(e))

# 用户登录
class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(body: UserLogin) -> dict:
    try:
        result = get_supabase().auth.sign_in_with_password({
            "email": body.email,
            "password": body.password
        })

        return {
            "user_id": result.user.id,
            "email": body.email,
            "role": result.user.user_metadata.get("role")
        }
    
    except Exception as e:
        raise HTTPException(400, str(e))
