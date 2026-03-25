from fastapi import APIRouter, Depends, HTTPException
from typing import List
from database import supabase
from models import ScoreCreate, Score
from routers.auth_router import get_current_user
from datetime import datetime

router = APIRouter()

@router.get("/scores", response_model=List[Score])
async def get_scores(current_user: dict = Depends(get_current_user)):
    result = supabase.table('scores').select('*').eq('user_id', current_user['id']).order('date', desc=True).execute()
    return result.data

@router.post("/scores", response_model=Score)
async def add_score(score: ScoreCreate, current_user: dict = Depends(get_current_user)):
    if not 1 <= score.score <= 45:
        raise HTTPException(status_code=400, detail="Score must be between 1 and 45")
    
    # Get current scores
    current_scores = supabase.table('scores').select('*').eq('user_id', current_user['id']).order('date', desc=True).execute()
    
    # If already 5 scores, remove oldest
    if len(current_scores.data) >= 5:
        oldest = current_scores.data[-1]
        supabase.table('scores').delete().eq('id', oldest['id']).execute()
    
    # Add new score
    score_data = {
        'user_id': current_user['id'],
        'score': score.score,
        'date': score.date.isoformat(),
        'created_at': datetime.utcnow().isoformat()
    }
    
    result = supabase.table('scores').insert(score_data).execute()
    return result.data[0]

@router.delete("/scores/{score_id}")
async def delete_score(score_id: int, current_user: dict = Depends(get_current_user)):
    score = supabase.table('scores').select('*').eq('id', score_id).eq('user_id', current_user['id']).execute()
    if not score.data:
        raise HTTPException(status_code=404, detail="Score not found")
    
    supabase.table('scores').delete().eq('id', score_id).execute()
    return {"message": "Score deleted"}