from fastapi import APIRouter, HTTPException, Request, Depends
from stripe_service import create_checkout_session
from dotenv import load_dotenv
import os
import stripe
from crud import change_property_status
from database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

load_dotenv()

router = APIRouter()

@router.post("/create_checkout_session/{property_id}")
async def pay_for_property(property_id:int,db:AsyncSession=Depends(get_db)):
    return await create_checkout_session(property_id,db)

@router.post("/webhook/stripe")
async def stripe_webhook(request:Request,db=Depends(get_db)):
    payload=await request.body()
    sig_header=request.headers["Stripe-Signature"]

    try:
        event=stripe.Webhook.construct_event(
            payload,
            sig_header,
            os.getenv("WEBHOOK_SECRET_KEY")
        )
    except stripe.error.SignatureVerificationError:
        return {"error":"Invalid Signature"}
    if event["type"]=="checkout.session.completed":
        session=event["data"]["object"]
        property_id=session.get("metadata").get("property_id")
        await change_property_status(db,property_id)


    return {"status":"success"}