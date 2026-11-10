from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import Product
from database import session, engine
import database_models
from sqlalchemy.orm import Session

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Create database tables
database_models.Base.metadata.create_all(bind=engine)


@app.get("/")
def greet():
    return "Welcome to Telusko Trac"

products = [
    Product(id=1, name="Laptop", description="A high-performance laptop", price=1299, quantity=10),
    Product(id=2, name="Mobile", description="A smartphone with great features", price=699, quantity=25),
    Product(id=3, name="Tablet", description="A lightweight tablet for everyday use", price=499, quantity=15),
    Product(id=4, name="Headphones", description="Noise-cancelling headphones", price=799, quantity=30)
]

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = session()

    count = db.query(database_models.Product).count()

    if count == 0:
        for product in products:
            db.add(database_models.Product(**product.model_dump()))
        db.commit()


init_db()



# GET: Fetch all products from PostgreSQL
@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):

    db_products = db.query(database_models.Product).all()
    return db_products


# GET: Fetch a single product
@app.get("/products/{id}")
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    try:
        product = db.query(database_models.Product).filter(
            database_models.Product.id == id
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        return product
    finally:
        db.close()


# POST: Insert a new product
@app.post("/products")
def add_product(product: Product , db: Session = Depends(get_db)):
    try:
        new_product = database_models.Product(**product.model_dump())

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product
    finally:
        db.close()


# PUT: Update an existing product
@app.put("/products/{id}")
def update_product(id: int, product: Product, db: Session = Depends(get_db)):
    try:
        existing_product = db.query(database_models.Product).filter(
            database_models.Product.id == id
        ).first()

        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")

        for key, value in product.model_dump().items():
            setattr(existing_product, key, value)

        db.commit()
        db.refresh(existing_product)

        return {"message": "Product updated successfully"}
    finally:
        db.close()


# DELETE: Delete a product
@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    try:
        product = db.query(database_models.Product).filter(
            database_models.Product.id == id
        ).first()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        db.delete(product)
        db.commit()

        return {"message": "Product deleted successfully"}
    finally:
        db.close()
