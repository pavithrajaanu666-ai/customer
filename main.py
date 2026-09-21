from fastapi import FastAPI, Request
from datetime import datetime, timedelta
from fastapi import HTTPException, Header
import jwt
import bcrypt
import mysql.connector
app = FastAPI()


# Database Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="jananijaanu",
    database="customer",
    port=3306
)

# ---------- Auth config ----------
SECRET_KEY = "change-this-to-a-long-random-secret"  # move to an env var before deploying
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60


def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Use 'Bearer <token>' in the Authorization header")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired, please log in again")
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or malformed token")


# ---------- Auth config ----------
SECRET_KEY = "change-this-to-a-long-random-secret"  # move to an env var before deploying
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60


def create_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Use 'Bearer <token>' in the Authorization header")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired, please log in again")
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or malformed token")


# ---------- Auth routes ----------
DEMO_USERNAME = "jaanu"
DEMO_PASSWORD = "test123"


@app.post('/api/login')  # log in, get back a JWT
async def login_user(request: Request):
    data = await request.json()
    username = data.get('username')
    password = data.get('password')

    if username != DEMO_USERNAME or password != DEMO_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token(username)
    return {"access_token": token, "token_type": "bearer"}


@app.post('/api/customers')  # create customer
async def create_user(request: Request):
    data = await request.json()
    # id = data.get('id')
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    created_at = data.get('created_at')

    cursor = mydb.cursor()
    sql = "INSERT INTO Customers (name,email,phone,created_at) VALUES(%s,%s,%s,now())"
    val = (name, email, phone)
    cursor.execute(sql, val)
    mydb.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return {
        "message": "Customer created succesfully",
        "id": new_id,
        "name": name,
        "email": email,
        "phone": phone,
        "created_at": created_at
    }


@app.get('/api/customers')  # list customers
async def list_customers():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM Customers")
    return cursor.fetchall()


@app.get('/api/customers/{id}')  # get customer
async def get_customer(id: int):
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM Customers WHERE id = %s", (id,))
    customer = cursor.fetchone()
    cursor.close()
    if not customer:
        print("Customer not found")
    return customer


@app.put('/api/customers/{id}')  # update customer
def update_customer(id: int, name: str):
    cursor = mydb.cursor()
    cursor.execute("UPDATE  Customers SET name = %s WHERE id =%s", (name, id))
    mydb.commit()
    updated = cursor.rowcount
    cursor.close()
    if updated == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"mesasage": "Customer updated succesfull"}
    pass


@app.delete('/api/customers/{id}')  # delete customer
def to_delete_customer(id: int):
    cursor = mydb.cursor()
    cursor.execute("DELETE from Customers WHERE id = %s", (id,))
    mydb.commit()
    deleted = cursor.rowcount
    cursor.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Succesfully deleted"}
    pass


@app.post('/api/orders')  # create order
async def to_create_order(request: Request):
    data = await request.json()
    # def to_create_order():
    customer_id = data.get('customer_id')
    order_number = data.get('order_number')
    amount = data.get('amount')
    status = data.get('status')

    cursor = mydb.cursor()
    sql = "INSERT INTO Orders (customer_id,order_number,amount,status) VALUES(%s,%s,%s,%s)"
    val = (customer_id, order_number, amount, status)
    cursor.execute(sql, val)
    mydb.commit()
    new_id = cursor.lastrowid
    cursor.close()
    return {
        # "id"=new_id
        "message": "Order  created succesfully",
        "customer_id": customer_id,
        "order_number": order_number,
        "amount": amount,
        "status": status
    }
    pass


@app.get('/api/orders')  # list the orders
def list_the_orders():
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM Orders")
    order = cursor.fetchall()
    cursor.close()
    return order
    pass


@app.get('/api/customers/{id}/orders')  # customer's order
def get_customers_orders(id: int):
    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM Orders WHERE customer_id = %s", (id,))
    coust_order = cursor.fetchall()
    cursor.close()
    return coust_order

    pass


@app.get('/api/customers/{id}/summary')  # customer summary
def get_customer_summary(id: int):
    cursor = mydb.cursor(dictionary=True)

    cursor.execute("SELECT id, name, email FROM Customers WHERE id = %s", (id,))
    customer = cursor.fetchone()
    if not customer:
        cursor.close()
        raise HTTPException(status_code=404, detail="Customer not found")

    cursor.execute("""
                   SELECT COUNT(*) AS order_count,
                          COALESCE(SUM(amount), 0) AS total_order_amount,
                          SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS completed_orders,
                          SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END)   AS pending_orders
                   FROM Orders
                   WHERE customer_id = %s
                   """, (id,))
    stats = cursor.fetchone()
    cursor.close()

    return {
        "customer": customer,
        "order_count": stats["order_count"],
        "total_order_amount": float(stats["total_order_amount"]),
        "completed_orders": int(stats["completed_orders"] or 0),
        "pending_orders": int(stats["pending_orders"] or 0)
    }


