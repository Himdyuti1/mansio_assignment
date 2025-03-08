from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import PropertyCreate,PropertyResponse,PropertyUpdate,PropertyRead
from crud import (
    create_property,
    get_property,
    get_all_properties,
    update_property,
    delete_property
)
from database import get_db

router=APIRouter()

@router.post("/post_property",response_model=PropertyResponse)
async def add_property(property_data:PropertyCreate,db:AsyncSession=Depends(get_db)):
    return await create_property(db,property_data)

@router.get("/get_property/{property_id}",response_model=dict)
async def get_property_endpoint(property_id:int,db:AsyncSession=Depends(get_db)):
    property_obj=await get_property(db,property_id)
    return {"property":property_obj}

@router.get("/get_all_properties",response_model=list)
async def get_all_properties_endpoint(db:AsyncSession=Depends(get_db)):
    properties=await get_all_properties(db)
    return properties

@router.put("/update_property/{property_id}",response_model=PropertyRead)
async def update_property_endpoint(property_id:int,property_update:PropertyUpdate,db:AsyncSession=Depends(get_db)):
    property_obj=await update_property(db,property_id,property_update)
    return PropertyRead.model_validate(property_obj, from_attributes=True) 

@router.delete("/delete_property/{property_id}")
async def delete_property_endpoint(property_id:int,db:AsyncSession=Depends(get_db)):
    result=await delete_property(db,property_id)
    return result