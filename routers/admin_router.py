from fastapi import APIRouter, Depends, HTTPException
from typing import List
from database import supabase
from models import User, Charity, CharityCreate, Draw, Winner
from routers.auth_router import get_current_user
from datetime import datetime

router = APIRouter()

def check_admin(current_user: dict = Depends(get_current_user)):
    if 'admin' not in current_user['email']:
        raise HTTPException(status_code=403, detail="Not authorized")
    return current_user

@router.get("/users")
async def get_users(current_user: dict = Depends(check_admin)):
    result = supabase.table('users').select('id,email,full_name,subscription_type,subscription_status,renewal_date,charity_id,created_at').execute()
    return result.data

@router.put("/users/{user_id}/subscription")
async def update_subscription(user_id: int, status: str, current_user: dict = Depends(check_admin)):
    if status not in ['active', 'inactive', 'lapsed']:
        raise HTTPException(status_code=400, detail="Invalid status")
    supabase.table('users').update({'subscription_status': status, 'updated_at': datetime.utcnow().isoformat()}).eq('id', user_id).execute()
    return {"message": f"Subscription updated to {status}"}

@router.get("/charities")
async def get_charities_admin(current_user: dict = Depends(check_admin)):
    result = supabase.table('charities').select('*').execute()
    return result.data

@router.post("/charities")
async def add_charity(charity: CharityCreate, current_user: dict = Depends(check_admin)):
    result = supabase.table('charities').insert({
        'name': charity.name,
        'description': charity.description,
        'image_url': charity.image_url,
        'website': charity.website,
        'created_at': datetime.utcnow().isoformat()
    }).execute()
    return result.data[0]

@router.delete("/charities/{charity_id}")
async def delete_charity(charity_id: int, current_user: dict = Depends(check_admin)):
    supabase.table('charities').delete().eq('id', charity_id).execute()
    return {"message": "Charity deleted"}

@router.get("/draws")
async def get_draws_admin(current_user: dict = Depends(check_admin)):
    result = supabase.table('draws').select('*').order('draw_date', desc=True).execute()
    return result.data

@router.get("/winners")
async def get_winners_admin(current_user: dict = Depends(check_admin)):
    result = supabase.table('winners').select('*').order('created_at', desc=True).execute()
    return result.data

@router.put("/winners/{winner_id}/verify")
async def verify_winner(winner_id: int, current_user: dict = Depends(check_admin)):
    winner = supabase.table('winners').select('*').eq('id', winner_id).execute()
    if not winner.data:
        raise HTTPException(status_code=404, detail="Winner not found")
    supabase.table('winners').update({'status': 'paid'}).eq('id', winner_id).execute()
    return {"message": "Winner verified and marked as paid"}

@router.put("/winners/{winner_id}/reject")
async def reject_winner(winner_id: int, current_user: dict = Depends(check_admin)):
    supabase.table('winners').update({'status': 'rejected'}).eq('id', winner_id).execute()
    return {"message": "Winner rejected"}

@router.get("/stats")
async def get_stats(current_user: dict = Depends(check_admin)):
    users = supabase.table('users').select('subscription_status, subscription_type').execute().data
    total_users = len(users)
    active_users = sum(1 for u in users if u['subscription_status'] == 'active')
    monthly_users = sum(1 for u in users if u['subscription_type'] == 'monthly' and u['subscription_status'] == 'active')
    yearly_users = sum(1 for u in users if u['subscription_type'] == 'yearly' and u['subscription_status'] == 'active')
    revenue = (monthly_users * 9.99) + (yearly_users * 99.99)

    draws = supabase.table('draws').select('id').execute().data
    winners = supabase.table('winners').select('prize_amount, status').execute().data
    total_paid = sum(w['prize_amount'] for w in winners if w['status'] == 'paid')

    return {
        "total_users": total_users,
        "active_users": active_users,
        "monthly_revenue": round(revenue, 2),
        "total_draws": len(draws),
        "total_prizes_paid": round(total_paid, 2)
    }
