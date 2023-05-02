import uvicorn as uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
import tokens
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

import jwt
from fastapi.security import OAuth2PasswordRequestForm

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware
origins = ["http://localhost", "http://localhost:8000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="templates")

# Serve static files from the "static" directory
static_path = str(Path(__file__).parent.absolute() / "templates")
app.mount("/static", StaticFiles(directory=f"{static_path}/"), name="static")


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


# Login endpoint
@app.post("/login")
async def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, login_data.email)
    if not user or not crud.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password")
    access_token = tokens.generate_token(user)
    response = JSONResponse({"access_token": access_token,
                             "message": "Login successfully",
                             "redirect_url": "/home",
                             "token-type": "bearer"}, status_code=200)
    return response


@app.get('/home', response_class=HTMLResponse)
async def get_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


def is_authenticated(request: Request):
    auth_header = request.headers.get("Authorization")
    scheme, token = auth_header.split()
    if not token:
        return False

    if scheme.lower() != "bearer":
        return False

    try:
        payload = tokens.decode_token(token)
        user_id = int(payload.get("sub"))
        request.state.user_id = user_id
        return True
    except (jwt.exceptions.InvalidTokenError, KeyError):
        return False

# Middleware to check validity of access token
# @app.middleware("http")
# async def check_token(request: Request, call_next):
#     if request.url.path == "/login":
#         return await call_next(request)
#
#     try:
#         auth_header = request.headers["Authorization"]
#         scheme, token = auth_header.split()
#         if scheme.lower() != "bearer":
#             raise HTTPException(status_code=401, detail="Invalid authentication credentials 1")
#     except (KeyError, ValueError):
#         # raise HTTPException(status_code=401, detail="Invalid authentication credentials 2")
#         response = RedirectResponse(url="/login", status_code=302)
#         return response
#     if token:
#         try:
#             payload = tokens.decode_token(token)
#             email: str
#         except (jwt.exceptions.InvalidTokenError, KeyError):
#             raise HTTPException(status_code=401, detail="Invalid authentication credentials 3")
#
#         request.state.user_id = payload.get("sub")
#     response = await call_next(request)
#     return response

# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
