def test_signup_and_login(client):
    # 1. Sign up new company admin
    signup_payload = {
        "name": "Dr. Aditi Rao",
        "email": "aditi@biopharma.com",
        "password": "SecurePassword123!",
        "role": "company_admin",
        "organization_name": "BioPharma Innovations",
        "licence_no": "LIC-TEST-999"
    }
    res = client.post("/api/v1/auth/signup", json=signup_payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "company_admin"
    assert data["organization_name"] == "BioPharma Innovations"

    # 2. Login with credentials
    login_payload = {
        "email": "aditi@biopharma.com",
        "password": "SecurePassword123!"
    }
    res_login = client.post("/api/v1/auth/login", json=login_payload)
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data

    # 3. Test me endpoint
    headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    res_me = client.get("/api/v1/auth/me", headers=headers)
    assert res_me.status_code == 200
    assert res_me.json()["email"] == "aditi@biopharma.com"

    # 4. Test token refresh
    res_refresh = client.post("/api/v1/auth/refresh", headers=headers)
    assert res_refresh.status_code == 200
    refresh_data = res_refresh.json()
    assert "access_token" in refresh_data
    assert refresh_data["user_id"] == data["user_id"]

    # 5. Test logout
    res_logout = client.post("/api/v1/auth/logout", headers=headers)
    assert res_logout.status_code == 200
    assert res_logout.json()["status"] == "success"


def test_invalid_login(client):
    login_payload = {
        "email": "nonexistent@pharma.com",
        "password": "WrongPassword"
    }
    res = client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == 401

