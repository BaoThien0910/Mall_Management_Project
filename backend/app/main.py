from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# --- CORS Configuration ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class LoginRequest(BaseModel):
    email: str
    password: str
    remember: Optional[bool] = False

# --- API Endpoints ---
@app.post("/api/login")
async def login(request: LoginRequest):
    # Our mock database with CHEAT CODES for ultra-fast testing!
    mock_users = {
        # Standard Accounts
        "admin@mainplaza.com": {"password": "admin123", "role": "admin"},
        "tenant@mainplaza.com": {"password": "tenant123", "role": "tenant"},
        "staff@mainplaza.com": {"password": "staff123", "role": "staff"},
        "board@mainplaza.com": {"password": "board123", "role": "management"},
        
        # 🌟 Cheat Code Accounts (Password is just "1") DELETE WHEN DONE
        "a": {"password": "1", "role": "admin"},
        "t": {"password": "1", "role": "tenant"},
        "s": {"password": "1", "role": "staff"},
        "b": {"password": "1", "role": "management"}
    }

    user = mock_users.get(request.email)

    if user and user["password"] == request.password:
        return {
            "token": f"super_secret_token_for_{user['role']}",
            "role": user["role"],
            "message": "Login successful"
        }
    else:
        raise HTTPException(
            status_code=401, 
            detail="Sai email hoặc mật khẩu!" 
        )