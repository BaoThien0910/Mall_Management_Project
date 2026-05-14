from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# 1. Allow React to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Your Vite React URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Define what the incoming data looks like
class LoginRequest(BaseModel):
    email: str
    password: str
    remember: bool

# 3. Create the Login Route
@app.post("/api/login")
async def login_user(request: LoginRequest):
    # This is a mock database check. We will add a real database later!
    if request.email == "admin@gmail.com" and request.password == "admin123":
        return {
            "status": "success",
            "message": "Login successful!",
            "token": "fake-jwt-token-12345"
        }
    else:
        # If the password is wrong, send back a 401 Unauthorized error
        raise HTTPException(status_code=401, detail="Invalid email or password")