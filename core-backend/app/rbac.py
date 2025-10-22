from fastapi import HTTPException, status

def require_roles(user_roles: list[str], required: list[str]):
    if not set(required).intersection(set(user_roles)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient_role")
