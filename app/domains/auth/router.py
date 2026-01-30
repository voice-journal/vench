# app/domains/auth/router.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.domains.auth.models import User, UserRole
from app.domains.auth.schema import UserCreate, UserLogin, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import EmailDuplicateException, UserNotFoundException, InvalidPasswordException

router = APIRouter()

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # 1. 이메일 중복 체크
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise EmailDuplicateException(email=user_in.email)

    # 2. 사용자 생성
    new_user = User(
        email=user_in.email,
        password=get_password_hash(user_in.password),
        nickname=user_in.nickname or user_in.email.split("@")[0],
        role=UserRole.USER
    )
    db.add(new_user)
    db.commit()
    return {"message": "회원가입 성공"}

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    # 1. 사용자 조회
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user:
        raise UserNotFoundException()

    # 2. 비밀번호 검증
    if not verify_password(user_in.password, user.password):
        raise InvalidPasswordException()

    # 3. 토큰 발급
    access_token = create_access_token(subject=user.id, role=user.role.value)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "nickname": user.nickname,
        "role": user.role
    }