from fastapi import APIRouter, Depends, HTTPException
from typing import List
from database import supabase
from models import Draw, Winner
from routers.auth_router import get_current_user
from datetime import datetime, date
import random

router = APIRouter()

SUBSCRIPTION_MONTHLY = 9.99
SUBSCRIPTION_YEARLY = 99.99
PRIZE_POOL_PERCENT = 0.40  # 40% of subscriptions go to prize pool

PRIZE_DISTRIBUTION = {5: 0.40, 4: 0.35, 3: 0.25}

@router.get("/draws", response_model=List[Draw])
async def get_draws():
    result = supabase.table('draws').select('*').order('draw_date', desc=True).execute()
    return result.data

@router.post("/draws/{draw_id}/enter")
async def enter_draw(draw_id: int, current_user: dict = Depends(get_current_user)):
    if current_user['subscription_status'] != 'active':
        raise HTTPException(status_code=403, detail="Active subscription required")

    draw = supabase.table('draws').select('*').eq('id', draw_id).execute()
    if not draw.data or draw.data[0]['status'] != 'pending':
        raise HTTPException(status_code=400, detail="Draw not available")

    scores = supabase.table('scores').select('score').eq('user_id', current_user['id']).order('date', desc=True).limit(5).execute()
    if len(scores.data) < 3:
        raise HTTPException(status_code=400, detail="Need at least 3 scores to enter draw")

    numbers = [s['score'] for s in scores.data]

    existing = supabase.table('draw_participants').select('id').eq('draw_id', draw_id).eq('user_id', current_user['id']).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Already entered this draw")

    supabase.table('draw_participants').insert({
        'draw_id': draw_id,
        'user_id': current_user['id'],
        'numbers': numbers,
        'created_at': datetime.utcnow().isoformat()
    }).execute()

    return {"message": "Successfully entered draw", "numbers": numbers}

@router.post("/draws", response_model=Draw)
async def create_draw(draw_date: date, current_user: dict = Depends(get_current_user)):
    if 'admin' not in current_user['email']:
        raise HTTPException(status_code=403, detail="Not authorized")

    numbers = sorted(random.sample(range(1, 46), 5))

    # Calculate prize pool from active subscriptions
    users = supabase.table('users').select('subscription_type').eq('subscription_status', 'active').execute()
    total_subs = sum(
        SUBSCRIPTION_YEARLY if u['subscription_type'] == 'yearly' else SUBSCRIPTION_MONTHLY
        for u in users.data
    )
    prize_pool = round(total_subs * PRIZE_POOL_PERCENT, 2)

    result = supabase.table('draws').insert({
        'draw_date': draw_date.isoformat(),
        'numbers': numbers,
        'status': 'pending',
        'prize_pool': prize_pool,
        'created_at': datetime.utcnow().isoformat()
    }).execute()
    return result.data[0]

@router.post("/draws/{draw_id}/publish")
async def publish_draw(draw_id: int, current_user: dict = Depends(get_current_user)):
    if 'admin' not in current_user['email']:
        raise HTTPException(status_code=403, detail="Not authorized")

    draw = supabase.table('draws').select('*').eq('id', draw_id).execute().data[0]
    draw_numbers = set(draw['numbers'])
    prize_pool = draw.get('prize_pool', 0)

    supabase.table('draws').update({'status': 'published'}).eq('id', draw_id).execute()

    participants = supabase.table('draw_participants').select('*').eq('draw_id', draw_id).execute().data

    winners_by_type = {5: [], 4: [], 3: []}
    for p in participants:
        user_numbers = set(p['numbers'])
        matches = len(draw_numbers & user_numbers)
        if matches >= 3:
            winners_by_type[matches].append(p['user_id'])

    for match_type, user_ids in winners_by_type.items():
        if not user_ids:
            continue
        pool_share = prize_pool * PRIZE_DISTRIBUTION[match_type]
        prize_per_winner = round(pool_share / len(user_ids), 2)
        for uid in user_ids:
            supabase.table('winners').insert({
                'draw_id': draw_id,
                'user_id': uid,
                'match_type': match_type,
                'prize_amount': prize_per_winner,
                'status': 'pending',
                'created_at': datetime.utcnow().isoformat()
            }).execute()

    return {"message": "Draw published and winners calculated", "prize_pool": prize_pool}

@router.get("/winners", response_model=List[Winner])
async def get_my_winners(current_user: dict = Depends(get_current_user)):
    result = supabase.table('winners').select('*').eq('user_id', current_user['id']).order('created_at', desc=True).execute()
    return result.data

@router.post("/winners/{winner_id}/proof")
async def upload_proof(winner_id: int, proof_url: str, current_user: dict = Depends(get_current_user)):
    winner = supabase.table('winners').select('*').eq('id', winner_id).eq('user_id', current_user['id']).execute()
    if not winner.data:
        raise HTTPException(status_code=404, detail="Winner record not found")
    supabase.table('winners').update({'proof_url': proof_url}).eq('id', winner_id).execute()
    return {"message": "Proof submitted successfully"}
