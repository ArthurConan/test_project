from typing import Dict


def test_get_access_token(client, random_user) -> None:
    r = client.post(
        "/api/auth/login/token",
        json={
            'email': random_user.email,
            'password': random_user.password
        }
    )
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_use_access_token(
    client, user_token_headers: Dict[str, str]
) -> None:
    r = client.post(
        "/api/auth/login/test-token", headers=user_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result

