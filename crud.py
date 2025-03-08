from sqlalchemy.ext.asyncio import AsyncSession
from models import Property
from schemas import PropertyCreate, PropertyUpdate, PropertyRead
from ai_utils import enhance_description,generate_keywords
from stripe_utils import create_product
from fastapi import HTTPException
from sqlalchemy.future import select
import pika
import json
from dotenv import load_dotenv
import os

load_dotenv()

RABBITMQ_HOST=os.getenv("RABBITMQ_HOST")

def sent_task_to_queue(queue_name,task):
    connection=pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel=connection.channel()
    channel.queue_declare(queue=queue_name,durable=True)

    message=json.dumps(task)
    channel.basic_publish(exchange="",routing_key=queue_name,body=message)
    connection.close()

async def create_property(db:AsyncSession,property_data:PropertyCreate):
    new_property=Property(
        title=property_data.title,
        description=property_data.description,
        price=property_data.price,
        status=property_data.status,
        ai_keywords=None,
        stripe_product_id=None
    )
    db.add(new_property)
    await db.commit()
    await db.refresh(new_property)

    sent_task_to_queue(
        "ai_tasks",
        {
            "task":"ai_enhancements",
            "title":property_data.title,
            "description":property_data.description,
            "property_id":new_property.id
        }
    )

    sent_task_to_queue(
        "stripe_tasks",
        {
            "task":"create_product",
            "property_id":new_property.id,
            "title":new_property.title,
            "price":new_property.price
        }
    )
    return f"Property {new_property.id} created successfully"


async def update_property(db:AsyncSession,property_id:int,update_data:PropertyUpdate):
    property_obj=await db.get(Property,property_id)
    if not property_obj:
        raise HTTPException(status_code=404,detail="Property not found")
    
    for key,value in update_data.model_dump(exclude_unset=True).items():
        setattr(property_obj,key,value)

    await db.commit()
    await db.refresh(property_obj)
    
    return property_obj

async def get_property(db:AsyncSession,property_id:int):
    property_obj=await db.get(Property,property_id)
    if not property_obj:
        raise HTTPException(status_code=404,detail="Property not found")
    return PropertyRead.model_validate(property_obj, from_attributes=True)

async def get_all_properties(db:AsyncSession):
    result=await db.execute(select(Property))
    properties=result.scalars().all()
    return [PropertyRead.model_validate(property, from_attributes=True) for property in properties]

async def delete_property(db:AsyncSession,property_id:int):
    property_obj=await db.get(Property,property_id)
    if not property_obj:
        raise HTTPException(status_code=404,detail="Property not found")
    await db.delete(property_obj)
    await db.commit()
    return {"message":f"Property {property_id} deleted successfully"}

async def change_property_status(db: AsyncSession, property_id: int):
    property_obj=await db.get(Property,int(property_id))
    if property_obj:
        property_obj.status = "paid"
        await db.commit()
        await db.refresh(property_obj)
    else:
        raise HTTPException(status_code=404, detail="Property not found")