import pytest
from fastapi import status
import json

def test_create_task(client):
    task_data = {
        "username": "testuser",
        "title": "New Test Task",
        "state": "todo"
    }
    
    response = client.post("/api/tasks/", json=task_data)
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["username"] == task_data["username"]
    assert data["state"] == task_data["state"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_get_all_tasks(client, sample_data):
    response = client.get("/api/tasks/")
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) == 3
    
    assert "id" in data[0]
    assert "title" in data[0]
    assert "state" in data[0]
    assert "username" in data[0]
    assert "created_at" in data[0]
    assert "updated_at" in data[0]

def test_get_tasks_by_username(client, sample_data):
    response = client.get("/api/tasks/?username=testuser")
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert len(data) == 2
    
    for task in data:
        assert task["username"] == "testuser"

def test_get_task_by_id(client, sample_data):
    task_id = sample_data["task1"]
    response = client.get(f"/api/tasks/{task_id}")
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task 1"
    assert data["username"] == "testuser"

def test_get_nonexistent_task(client):
    response = client.get("/api/tasks/9999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_task(client, sample_data):
    task_id = sample_data["task1"]
    
    update_data = {
        "title": "Updated Task Title",
        "state": "done"
    }
    
    response = client.put(
        f"/api/tasks/{task_id}", 
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == update_data["title"]
    assert data["state"] == update_data["state"]
    assert data["username"] == "testuser"

def test_update_task_wrong_username(client, sample_data):
    non_existent_task_id = 9999
    
    update_data = {
        "title": "Updated Task Title", 
        "state": "done"
    }
    
    response = client.put(
        f"/api/tasks/{non_existent_task_id}", 
        json=update_data
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_task(client, sample_data):
    task_id = sample_data["task2"]
    
    response = client.delete(f"/api/tasks/{task_id}")
    
    assert response.status_code == status.HTTP_200_OK
    
    get_response = client.get(f"/api/tasks/{task_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_task_wrong_username(client, sample_data):
    non_existent_task_id = 9999
    
    response = client.delete(f"/api/tasks/{non_existent_task_id}")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
