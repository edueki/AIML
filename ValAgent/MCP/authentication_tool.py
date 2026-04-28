from models import AuthValidateResponse
from server import mcp, http_post
from typing import Annotated, Dict, Any
from config import  AUTH_URL

@mcp.tool(
    name="validate_auth_token",
    description=(
    "Validate a bearer JWT token to confirm authentication status and extract the "
    "currently logged-in user's identity (subject), along with token validity, "
    "issued-at time, and expiration time."
    )
)
async def validate_auth_token(
    bearer_token: Annotated[str, "JWT token to validate"]
) -> AuthValidateResponse:
    """
    Calls POST /auth/validate with:
      Authorization: Bearer <token>

    Returns:
      {
        "valid": bool,
        "sub": str,
        "iat": int,
        "exp": int
      }
    """

    resp = await http_post(
        AUTH_URL,
        headers={
            "accept": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        },
        body={}  # validation API usually requires empty JSON body
    )

    return AuthValidateResponse(**resp)
