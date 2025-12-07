from fastapi.testclient import TestClient


def test_create_blog_pending_status(client: TestClient, user_token: str):
    # Create a blog as normal user
    res = client.post(
        "/api/blogs/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"title": "Test Blog", "content": "Hello World"},
    )
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["title"] == "Test Blog"
    assert data["status"] == "pending"
    assert "id" in data
    blog_id = data["id"]

    # Public list should not show it yet (only approved)
    res_public = client.get("/api/blogs/")
    assert res_public.status_code == 200
    assert all(b["id"] != blog_id for b in res_public.json())


def test_admin_can_approve_blog(client: TestClient, user_token: str, admin_token: str):
    # User creates a pending blog
    res = client.post(
        "/api/blogs/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"title": "Blog To Approve", "content": "Approve me"},
    )
    assert res.status_code == 201, res.text
    blog = res.json()
    blog_id = blog["id"]
    assert blog["status"] == "pending"

    # Admin sees it in pending list
    res_pending = client.get(
        "/api/blogs/pending",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_pending.status_code == 200, res_pending.text
    pending_ids = [b["id"] for b in res_pending.json()]
    assert blog_id in pending_ids

    # Admin approves it
    res_approve = client.post(
        f"/api/blogs/{blog_id}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res_approve.status_code == 200, res_approve.text
    approved = res_approve.json()
    assert approved["status"] == "approved"

    # Now it appears in public list
    res_public = client.get("/api/blogs/")
    assert res_public.status_code == 200
    public_ids = [b["id"] for b in res_public.json()]
    assert blog_id in public_ids
