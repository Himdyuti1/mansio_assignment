from sqlalchemy.ext.asyncio import AsyncSession
from models import Property
from schemas import PropertyCreate, PropertyUpdate, PropertyRead
from ai_utils import enhance_description,generate_keywords
from stripe_service import create_product
from fastapi import HTTPException
from sqlalchemy.future import select

async def create_property(db:AsyncSession,property_data:PropertyCreate):
    enhanced_description=await enhance_description(property_data.title,property_data.description or "")
    ai_keywords=await generate_keywords(property_data.title,property_data.description or "")

    new_property=Property(
        title=property_data.title,
        description=enhanced_description,
        price=property_data.price,
        status=property_data.status,
        ai_keywords=ai_keywords,
        stripe_product_id=None
    )
    db.add(new_property)
    await db.commit()
    await db.refresh(new_property)

    try:
        stripe_product_id,_=await create_product(id=new_property.id,title=new_property.title,price=new_property.price)
        new_property.stripe_product_id=stripe_product_id
        await db.commit()
        await db.refresh(new_property)
        return new_property
    except Exception as e:
        await delete_property(db,new_property.id)
        raise HTTPException(status_code=400,detail=str(e))


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
    return property_obj

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