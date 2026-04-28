from server import mcp
from config import REG_URL
from server import http_get, http_post
from typing import Any, Dict, Annotated
from pydantic import EmailStr, Field

@mcp.tool(name="signup",description= "Create a new user account")
async def auth_signup(email: EmailStr, password: str, name: str) -> Dict[str, Any]:
    """
    Register a new user account.
    Inputs: email (EmailStr), password (6-128 chars), name (str).
    Returns the API's structured response: {ok, status_code, data|error}.
    """
    url = f"{REG_URL.rstrip('/')}/signup"
    body = {"email": email, "password": password, "name": name}
    return await http_post(url, body=body)

@mcp.tool(name="signin", description= "Create a bearer token and return the token for authentication.")
async def auth_signin(email: EmailStr, password: str) -> Dict[str, Any]:
    """
    Sign in with email and password.
    Returns a bearer token and user info if successful.
    """
    url = f"{REG_URL.rstrip('/')}/login"
    body = {"email": email, "password": password}
    return await http_post(url, body=body)