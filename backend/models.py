from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, TIMESTAMP, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Role(Base):
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String, nullable=False, unique=True)
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    phone_number = Column(String)
    role_id = Column(Integer, ForeignKey("roles.role_id"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    role = relationship("Role", back_populates="users")
    products = relationship("Product", back_populates="vendor")
    orders = relationship("Order", back_populates="customer")

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String, nullable=False)
    description = Column(Text)
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    description = Column(Text)
    base_price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    vendor_id = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    category = relationship("Category", back_populates="products")
    vendor = relationship("User", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)

class Inventory(Base):
    __tablename__ = "inventory"
    inventory_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"))
    stock_quantity = Column(Integer, nullable=False)
    warehouse_location = Column(String)
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    product = relationship("Product", back_populates="inventory")

class Order(Base):
    __tablename__ = "orders"
    order_id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.user_id"))
    order_date = Column(TIMESTAMP, server_default=func.now())
    total_amount = Column(Numeric(10, 2), default=0.00)
    status = Column(String, default="Pending")

    customer = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payment = relationship("Payment", back_populates="order", uselist=False)
    shipping = relationship("ShippingDetail", back_populates="order", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"
    order_item_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")

class Payment(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    payment_method = Column(String)
    transaction_id = Column(String, unique=True)
    amount_paid = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String, default="Completed")

    order = relationship("Order", back_populates="payment")

class Review(Base):
    __tablename__ = "reviews"
    review_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.product_id"))
    customer_id = Column(Integer, ForeignKey("users.user_id"))
    rating = Column(Integer)
    comment = Column(Text)
    review_date = Column(TIMESTAMP, server_default=func.now())

class ShippingDetail(Base):
    __tablename__ = "shipping_details"
    shipping_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    shipping_address = Column(Text, nullable=False)
    city = Column(String, nullable=False)
    tracking_number = Column(String, unique=True)
    estimated_delivery = Column(Date)

    order = relationship("Order", back_populates="shipping")