import pika
import json
from dotenv import load_dotenv
import os
import cohere
from database import get_db
from ai_utils import enhance_description,generate_keywords
from models import Property
import asyncio

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
RABBITMQ_HOST="localhost"

conn=cohere.Client(COHERE_API_KEY)

MIN_WORDS=20
WORD_LIMIT=50

async def process_ai_task(ch,method,properties,body):
    task=json.loads(body)  

    print(f"Processing AI Task for Property ID: {task['property_id']}")
    async for db in get_db():
        try:
            property_obj=await db.get(Property,task["property_id"])
            if not property_obj:
                raise Exception("Property not found")
            if task["task"]=="ai_enhancements":
                enhanced_description=await enhance_description(task["title"],task["description"])
                property_obj.description=enhanced_description
                ai_keywords=await generate_keywords(task["title"],enhanced_description)
                property_obj.ai_keywords=ai_keywords
                await db.commit()
                await db.refresh(property_obj)
            print("AI Task Processed Successfully")
        except Exception as e:
            print(f"Error processing AI task: {str(e)}")
        break

def callback_wrapper(ch, method, properties, body):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(process_ai_task(ch, method, properties, body))
    else:
        loop.run_until_complete(process_ai_task(ch, method, properties, body))

connection=pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel=connection.channel()
channel.queue_declare(queue="ai_tasks",durable=True)
channel.basic_consume(queue="ai_tasks",on_message_callback=callback_wrapper,auto_ack=True)

print("AI Worker Started...")
channel.start_consuming()