from typing import List
from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def read_root():
    return RedirectResponse("/login", status_code=302)

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get('/login', response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login-form.html", {"request": request})

@app.post('/login')
async def login(
    db: Session = Depends(get_db), 
    username: str = Form(...), 
    password: str = Form(...),
    next: str = Form()
    ):
    db_user = crud.get_user_by_email(db, email=username)
    if not db_user:
        return JSONResponse({"success": False, "message": "Email is not existed", "redirect_url": None})
    
    fake_hashed_password = password + "notreallyhashed"
    if not (fake_hashed_password == db_user.hashed_password):
        return JSONResponse({"success": False, "message": "Invalid login credentials", "redirect_url": None})
    
    return JSONResponse({"success": True, "message": "Login successful", "redirect_url": next})


@app.get('/home', response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})
