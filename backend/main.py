from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="E-Commerce API")

@app.get("/")
def get_message():
    return "Success"

@app.get("/roles")
def get_roles(db: Session = Depends(database.get_db)):
    return db.query(models.Role).all()


@app.get("/users")
def get_users(db: Session = Depends(database.get_db)):
    return db.query(models.User).all()


@app.get("/categories")
def get_categories(db: Session = Depends(database.get_db)):
    return db.query(models.Category).all()


@app.get("/products")
def get_products(db: Session = Depends(database.get_db)):
    return db.query(models.Product).all()


@app.get("/inventory")
def get_inventory(db: Session = Depends(database.get_db)):
    return db.query(models.Inventory).all()

@app.get("/orders")
def get_orders(db: Session = Depends(database.get_db)):
    return db.query(models.Order).all()


@app.get("/order-items")
def get_order_items(db: Session = Depends(database.get_db)):
    return db.query(models.OrderItem).all()


@app.get("/payments")
def get_payments(db: Session = Depends(database.get_db)):
    return db.query(models.Payment).all()


@app.get("/reviews")
def get_reviews(db: Session = Depends(database.get_db)):
    return db.query(models.Review).all()


@app.get("/shipping")
def get_shipping(db: Session = Depends(database.get_db)):
    return db.query(models.ShippingDetail).all()


@app.get("/dashboard/summary")
def get_summary(db: Session = Depends(database.get_db)):
    from sqlalchemy import func
    total_sales = db.query(func.sum(models.Order.total_amount)).scalar() or 0
    total_products = db.query(models.Product).count()
    low_stock = db.query(models.Inventory).filter(models.Inventory.stock_quantity < 20).count()
    
    return {
        "revenue": float(total_sales),
        "product_count": total_products,
        "low_stock_alerts": low_stock
    }

class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    base_price: Optional[float] = None
    description: Optional[str] = None

@app.put("/products/{product_id}")
def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(database.get_db)):
    db_product = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product_data.product_name:
        db_product.product_name = product_data.product_name
    if product_data.base_price:
        db_product.base_price = product_data.base_price
    if product_data.description:
        db_product.description = product_data.description

    db.commit()
    return {"message": f"Product {product_id} updated successfully"}


class ProductCreate(BaseModel):
    product_name: str
    description: str
    base_price: float
    category_id: int
    vendor_id: int
    stock: int


@app.post("/products/create")
def create_product(product: ProductCreate, db: Session = Depends(database.get_db)):
    # 1. Add to Products table
    new_prod = models.Product(
        product_name=product.product_name,
        description=product.description,
        base_price=product.base_price,
        category_id=product.category_id,
        vendor_id=product.vendor_id
    )
    db.add(new_prod)
    db.commit()
    db.refresh(new_prod)
    
    new_inv = models.Inventory(product_id=new_prod.product_id, stock_quantity=product.stock)
    db.add(new_inv)
    db.commit()
    return {"message": "Product created successfully", "id": new_prod.product_id}


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db)):
    prod = db.query(models.Product).filter(models.Product.product_id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(prod)
    db.commit()
    return {"message": f"Product {product_id} deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)