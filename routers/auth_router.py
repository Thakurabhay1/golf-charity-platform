from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import supabase
from models import UserCreate, UserLogin, User, Token
from auth import get_password_hash, verify_password, create_access_token
from datetime import datetime

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    from auth import verify_token
    token_data = verify_token(token, credentials_exception)
    user = supabase.table('users').select('*').eq('email', token_data.email).execute()
    if not user.data:
        raise credentials_exception
    return user.data[0]

@router.post("/signup", response_model=User)
async def signup(user: UserCreate):
    # Check if user exists
    existing = supabase.table('users').select('*').eq('email', user.email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user
    user_data = {
        'email': user.email,
        'password_hash': hashed_password,
        'full_name': user.full_name,
        'subscription_type': user.subscription_type,
        'subscription_status': 'active',
        'charity_id': user.charity_id,
        'contribution_percentage': user.contribution_percentage,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }
    
    result = supabase.table('users').insert(user_data).execute()
    return result.data[0]

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = supabase.table('users').select('*').eq('email', form_data.username).execute()
    if not user.data:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    user = user.data[0]
    if not verify_password(form_data.password, user['password_hash']):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user['email']})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user