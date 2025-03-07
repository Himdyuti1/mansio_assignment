from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from crud import (
    create_property,
    get_property,
    get_all_properties,
    update_property,
    delete_property
)
from schemas import PropertyCreate,PropertyResponse,PropertyUpdate,PropertyRead
from stripe_service import process_payment

app = FastAPI(title="Mansio AI Backend")

@app.get("/")
async def root():
    return {"message": "Welcome to Mansio AI Backend!"}

@app.post("/post_property",response_model=PropertyResponse)
async def add_property(property_data:PropertyCreate,db:AsyncSession=Depends(get_db)):
    return await create_property(db,property_data)

@app.get("/get_property/{property_id}",response_model=dict)
async def get_property_endpoint(property_id:int,db:AsyncSession=Depends(get_db)):
    property_obj=await get_property(db,property_id)
    return {"property":property_obj}

@app.get("/get_all_properties",response_model=list)
async def get_all_properties_endpoint(db:AsyncSession=Depends(get_db)):
    properties=await get_all_properties(db)
    return properties

@app.put("/update_property/{property_id}",response_model=PropertyRead)
async def update_property_endpoint(property_id:int,property_update:PropertyUpdate,db:AsyncSession=Depends(get_db)):
    property_obj=await update_property(db,property_id,property_update)
    return PropertyRead.model_validate(property_obj, from_attributes=True) 

@app.delete("/delete_property/{property_id}")
async def delete_property_endpoint(property_id:int,db:AsyncSession=Depends(get_db)):
    result=await delete_property(db,property_id)
    return result

@app.post("/pay/{property_id}")
async def pay_for_property(property_id:int,email:str):
    result=process_payment(property_id,email)
    if result["status"]=="success":
        return {"message":"Payment successful","payment_id":result["payment_id"]}
    raise HTTPException(status_code=400,detail=result["error"])