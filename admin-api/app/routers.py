import os
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import select, delete
from app.database import async_session
from app.models import Product, Lead

router = APIRouter()
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")


def verify_token(authorization: str = Header(None)):
    if authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")


class ProductIn(BaseModel):
    name: str
    description: str | None = None
    price: float | None = None
    category: str | None = None


@router.get("/products", dependencies=[Depends(verify_token)])
async def list_products():
    async with async_session() as s:
        res = await s.execute(select(Product).order_by(Product.id))
        return [{
            "id": p.id, "name": p.name, "description": p.description,
            "price": float(p.price) if p.price else None, "category": p.category,
        } for p in res.scalars().all()]


@router.post("/products", dependencies=[Depends(verify_token)])
async def create_product(data: ProductIn):
    async with async_session() as s:
        p = Product(**data.model_dump())
        s.add(p)
        await s.commit()
        await s.refresh(p)
        return {"id": p.id, "status": "created"}


@router.delete("/products/{product_id}", dependencies=[Depends(verify_token)])
async def remove_product(product_id: int):
    async with async_session() as s:
        await s.execute(delete(Product).where(Product.id == product_id))
        await s.commit()
        return {"status": "deleted"}


@router.get("/leads", dependencies=[Depends(verify_token)])
async def list_leads():
    async with async_session() as s:
        res = await s.execute(select(Lead).order_by(Lead.created_at.desc()))
        return [{
            "id": l.id, "telegram_id": l.telegram_id, "username": l.username,
            "name": l.name, "phone": l.phone, "notes": l.notes,
            "created_at": str(l.created_at),
        } for l in res.scalars().all()]