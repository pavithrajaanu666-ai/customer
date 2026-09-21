import requests


BASE_URL = "http://localhost:8000"
def main():
    # 1. Login
    res = requests.post(f"{BASE_URL}/api/login", json={"username": "jaanu", "password": "test123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("1. Login successful:", token[:20], "...")

    # 2. Create a Customer
    res = requests.post(f"{BASE_URL}/api/customers",
                        json={"name": "Ramesh Kumar", "email": "ramesh@example.com", "phone": "9876543210"},
                        headers=headers)
    customer_id = res.json()["id"]
    print("2. Customer Created, ID:", customer_id)

    # 3. Fetch Customers
    res = requests.get(f"{BASE_URL}/api/customers", headers=headers)
    print("3. All Customers:", res.json())

    # 4. Create an Order
    res = requests.post(f"{BASE_URL}/api/orders",
                        json={"customer_id": customer_id, "order_number": 1001, "amount": 1500,
                              "status": "pending"}, headers=headers)
    print("4. Order Created:", res.json())

    # 5. Fetch the Customer's Orders
    res = requests.get(f"{BASE_URL}/api/customers/{customer_id}/orders", headers=headers)
    print("5. Customer Orders:", res.json())

    # 6. Update the Customer
    res = requests.put(f"{BASE_URL}/api/customers/{customer_id}", params={"name": "Ramesh K."}, headers=headers)
    print("6. Customer Updated:", res.json())

    # 7. Delete the Customer
    res = requests.delete(f"{BASE_URL}/api/customers/{customer_id}", headers=headers)
    print("7. Customer Deleted:", res.json())

    # 8. Handle API Errors
    res = requests.delete(f"{BASE_URL}/api/customers/{customer_id}", headers=headers)  # delete again → 404
    print("8a. Error - Delete again (expect 404):", res.status_code, res.json())

    res = requests.post(f"{BASE_URL}/api/login",
                        json={"username": "jaanu", "password": "wrongpass"})  # wrong password → 401
    print("8b. Error - Wrong password (expect 401):", res.status_code, res.json())
if __name__== "__main__":
    main()