from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from routers import auth_router, scores_router, charities_router, draws_router, admin_router

app = FastAPI(title="GolfGives", description="Golf Charity Subscription Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(scores_router.router, prefix="/api", tags=["scores"])
app.include_router(charities_router.router, prefix="/api", tags=["charities"])
app.include_router(draws_router.router, prefix="/api", tags=["draws"])
app.include_router(admin_router.router, prefix="/admin", tags=["admin"])

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.get("/signup")
async def signup_page(request: Request):
    return templates.TemplateResponse(request, "signup.html")

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "dashboard.html")

@app.get("/admin")
async def admin_page(request: Request):
    return templates.TemplateResponse(request, "admin.html")

@app.get("/logout")
async def logout():
    return RedirectResponse(url="/")
