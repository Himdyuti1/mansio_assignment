import stripe
import os
from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db 
from models import Property
from sqlalchemy.future import select

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

async def create_product(id:int,title:str,price:float)->str:
    product=stripe.Product.create(
        name=title,
        metadata={
            "property_id":id
        }
    )
    price_obj=stripe.Price.create(
        unit_amount=int(price*100),
        currency="inr",
        product=product.id
    )
    return product.id,price_obj.id

async def create_checkout_session(property_id: int, db: AsyncSession):
    result = await db.execute(select(Property).where(Property.id == property_id))
    property_obj = result.scalars().first()
    stripe_price_id=stripe.Price.list(product=property_obj.stripe_product_id,active=True).data[0].id
    if not property_obj or not property_obj.stripe_product_id:
        return {"error": "Property or associated Stripe price not found"}

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        currency="inr",
        line_items=[
            {
                "price": stripe_price_id,
                "quantity": 1
            }
        ],
        mode="payment",
        metadata={
            "property_id": property_id
        },
        billing_address_collection="required",
        success_url=f"http://localhost:8000/success/{property_id}",
        cancel_url=f"http://localhost:8000/cancel/{property_id}"
    )
    return session.url