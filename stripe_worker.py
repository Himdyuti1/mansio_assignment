import pika
import json
from database import get_db
from stripe_utils import create_product
from models import Property
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

RABBITMQ_HOST=os.getenv("RABBITMQ_HOST")

async def process_stripe_task(ch,method,properties,body):
    task=json.loads(body)

    print(f"Processing Stripe Task for Property ID: {task['property_id']}")
    async for db in get_db():
        try:
            property_obj=await db.get(Property,task["property_id"])
            if not property_obj:
                raise Exception("Property not found")
            
            if task["task"]=="create_product":
                stripe_product_id,_=await create_product(id=task["property_id"],title=task["title"],price=task["price"])
                property_obj.stripe_product_id=stripe_product_id
                await db.commit()
                await db.refresh(property_obj)
            print("Stripe Task Processed Successfully")

        except Exception as e:
            print(f"Error processing Stripe task: {str(e)}")
        break

def callback_wrapper(ch, method, properties, body):
    loop = asyncio.get_event_loop()
    if loop.is_running():  # Use existing event loop
        loop.create_task(process_stripe_task(ch, method, properties, body))
    else:
        loop.run_until_complete(process_stripe_task(ch, method, properties, body))
    
connection=pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel=connection.channel()
channel.queue_declare(queue="stripe_tasks",durable=True)
channel.basic_consume(queue="stripe_tasks",on_message_callback=callback_wrapper,auto_ack=True)

print("Stripe Worker Started...")
channel.start_consuming()