from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
import tokens
from starlette.status import HTTP_401_UNAUTHORIZED
import jwt

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency to provide a database session object
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
    user = crud.get_user_by_email(db, email=username)

    fake_hashed_password = password + "notreallyhashed"
    if not user or fake_hashed_password != user.hashed_password:
        return JSONResponse(content={"success": False, "message": "Incorrect username or password", "redirect_url": None}, 
                            status_code=HTTP_401_UNAUTHORIZED)
    
    # Generate a JWT containing the user ID and an expiration time
    token = tokens.generate_token(user)
    
    response = JSONResponse(content={"success": True, "message": "Login successfully", "redirect_url": next},
                            status_code=200)
    # Set the token as a cookie in the response
    response.set_cookie(key="access_token", value=token)

    return response

@app.get('/home', response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

def is_authenticated(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return False
    
    try:
        payload = tokens.decode_token(token)
        user_id = int(payload["sub"])
        print("user_id ", user_id)
        print("user_id type ", type(user_id))
        request.state.user_id = user_id
        return True
    except (jwt.exceptions.InvalidTokenError, KeyError):
        return False


@app.middleware("http")
async def middleware(request: Request, call_next):
    if not is_authenticated(request):
        if request.url.path not in ["/login", "/docs"]:
            return RedirectResponse(url="/login")
    response = await call_next(request)
    return response
