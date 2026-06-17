# app/utils/util.py
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, TypeVar

from flask.typing import ResponseReturnValue
from jose import jwt
import jose
from functools import wraps
from flask import request, jsonify

SECRET_KEY = "a super secret, secret key"
R = TypeVar("R")

def encode_token(user_id: int | str) -> str:  # using unique info to make tokens user specific
    payload: dict[str, datetime | str] = {
        "exp": datetime.now(timezone.utc) + timedelta(days=0, hours=1),
        "iat": datetime.now(timezone.utc),
        "sub": str(user_id),
    }

    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def token_required(f: Callable[..., R | ResponseReturnValue]) -> Callable[..., R | ResponseReturnValue]:
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> R | ResponseReturnValue:
        token: str | None = None
        # Look for the token in the Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            parts = auth_header.split(" ", maxsplit=1)
            if len(parts) == 2:
                token = parts[1]
        
        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = str(data["sub"])
            
        except jose.exceptions.ExpiredSignatureError:
             return jsonify({"message": "Token has expired!"}), 401
        except jose.exceptions.JWTError:
             return jsonify({"message": "Invalid token!"}), 401

        return f(user_id, *args, **kwargs)

    return decorated