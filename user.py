# from fastapi import APIRouter
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.models import User
from app.scahmes import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
import slugify

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/all_users")
async def all_users(db: Annotated[Session, Depends(get_db())]):
    users_query = db.scalars(select(User))
    return [user for user in users_query.all]


@router.get("/user_id/{user_id}")
async def user_by_id(user_id: int, db: Annotated[Session, Depends(get_db)]):
    user_query = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    if user_query is None:
        raise HTTPException(status_code=404, detail="User was not found")

    return user_query


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(create_user: CreateUser, db: Annotated[Session, Depends(get_db)]):
    new_user = User(
        username=create_user.username,
        firstname=create_user.firstname,
        lastname=create_user.lastname,
        age=create_user.age
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}
    except Exception as e:
        # Обработка возможных исключений, например, уникальности поля username
        print(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {e}")


@router.put("/update/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, update_user: UpdateUser, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.query(User).filter(User.id == user_id).first()

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    existing_user.username = update_user.username
    existing_user.firstname = update_user.firstname
    existing_user.lastname = update_user.lastname
    existing_user.age = update_user.age

    db.commit()

    return {"status_code": status.HTTP_200_OK, "transaction": "User update is successful!"}

@router.delete("/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    existing_user = db.query(User).filter(User.id == user_id).first()

    if existing_user is None:
        raise HTTPException(status_code=404, detail="User was not found")

    db.delete(existing_user)
    db.commit()

    return {"status_code": status.HTTP_204_NO_CONTENT, "transaction": "User deleted successfully!"}
