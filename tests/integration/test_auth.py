async def test_register(client):
    payload = {"email": "test_email1@email.com", "password": "password"}

    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test_email1@email.com"

async def test_existing_email(client):
    payload = {"email": "test_email2@email.com", "password": "password"}

    response1 = await client.post("/auth/register", json=payload)
    response2 = await client.post("/auth/register", json=payload)

    assert response2.status_code == 400

async def test_valid_email(client):
    payload = {"email": "test_email3", "password": "password"}

    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 422

async def test_login(client):
    payload1 = {"email":"test_email4@email.com", "password":"password"}
    payload2 = {"username":"test_email4@email.com", "password":"password"}

    response = await client.post("/auth/register", json=payload1)
    response = await client.post("/auth/login", data=payload2)

    assert response.status_code == 200
    assert response.json()["access_token"]

async def test_not_existing_email(client):
    payload = {"username": "test_email5@email.com", "password":"password"}

    response = await client.post("/auth/login", data=payload)

    assert response.status_code == 401

async def test_incorrect_password(client):
    payload1 = {"email": "test_email6@email.com", "password": "correct_password"}
    payload2 = {"username": "test_email6@email.com", "password": "incorrect_password"}

    response1 = await client.post("/auth/register", json=payload1)
    response2 = await client.post("/auth/login", data=payload2)

    assert response2.status_code == 401

# Запустить тесты (с запущенными контейнерами):
# docker compose run --rm -v \
#       $(pwd)/tests:/app/tests -v \
#       $(pwd)/pyproject.toml:/app/pyproject.toml \
#       web pytest tests/integration/test_auth.py -v