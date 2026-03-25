from fastapi import APIRouter, HTTPException
from typing import List
from database import supabase
from models import Charity

router = APIRouter()

@router.get("/charities", response_model=List[Charity])
async def get_charities():
    result = supabase.table('charities').select('*').execute()
    return result.data

@router.get("/charities/{charity_id}", response_model=Charity)
async def get_charity(charity_id: int):
    result = supabase.table('charities').select('*').eq('id', charity_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Charity not found")
    return result.data[0]