from __future__ import annotations

import jwt
from fastapi import Header


def get_user_email(authorization: str = Header(...)) -> str:
    """Get the user email from the authorization header."""
    return jwt.decode(authorization, options={"verify_signature": False})[
        "cognito:username"
    ]
