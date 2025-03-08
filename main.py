from fastapi import FastAPI
from routers.property_routers import router as property_router
from routers.stripe_routers import router as stripe_router

app = FastAPI(title="Mansio AI Backend")
app.include_router(property_router)
app.include_router(stripe_router)

@app.get("/")
async def root():
    return {"message": "Welcome to Mansio AI Backend!"}

@app.get("/success/{property_id}")
async def success(property_id:int):
    return {"message": f"Property {property_id} payment successful"}

@app.get("/cancel/{property_id}")
async def cancel(property_id:int):
    return {"message": f"Property {property_id} payment cancelled"}