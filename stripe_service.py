import stripe
import os
from dotenv import load_dotenv

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

def get_product_price(product_id:str)->int:
    price=stripe.Price.list(product=product_id,active=True)
    try:
        if price["data"]:
            return price["data"][0]["unit_amount"]/100
        return None
    except stripe.error.StripeError as e:
        print(e)
        return None

def process_payment(product_id:str,customer_email:str):
    amount=get_product_price(product_id)
    if amount is None:
        return {"error":"Product not found"}
    try:
        payment_intent=stripe.PaymentIntent.create(
            amount=int(amount*100),
            currency="inr",
            receipt_email=customer_email,
            payment_method_types=["card"],
            confirm=True
        )
        return {"status":"success","payment_id":payment_intent.id}
    except stripe.error.StripeError as e:
        return {"status":"failed","error":str(e)}