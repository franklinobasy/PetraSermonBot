import pytest
from pymongo import MongoClient
from database.mongodb.models import Sermon
from database.mongodb.utils import upload_sermon, get_sermon, update_sermon, delete_sermon
from database.mongodb import docs_store_collection


def test_upload_sermon():
    sermon_id = upload_sermon(
        title="Test Sermon",
        cover_url="https://example.com/cover.jpg",
        document_url="https://example.com/document.pdf",
        minister="Test Minister",
        description="This is a test sermon.",
    )
    assert sermon_id is not None

    # Check if the document is in the collection
    document = docs_store_collection.find_one({"sermon_id": sermon_id})
    assert document is not None


def test_get_sermon():
    # Upload a test sermon
    sermon_id = upload_sermon(
        title="Test Sermon",
        cover_url="https://example.com/cover.jpg",
        document_url="https://example.com/document.pdf",
        minister="Test Minister",
        description="This is a test sermon.",
    )

    # Test retrieval by sermon_id
    retrieved_sermon = get_sermon("sermon_id", sermon_id)
    assert retrieved_sermon is not None
    assert retrieved_sermon["sermon_id"] == sermon_id

    # Test retrieval by title
    retrieved_sermon_by_title = get_sermon("title", "Test Sermon")
    assert retrieved_sermon_by_title is not None
    assert retrieved_sermon_by_title["title"] == "Test Sermon"


def test_update_sermon():
    # Upload a test sermon
    sermon_id = upload_sermon(
        title="Test Sermon",
        cover_url="https://example.com/cover.jpg",
        document_url="https://example.com/document.pdf",
        minister="Test Minister",
        description="This is a test sermon.",
    )

    # Update the sermon
    updated_data = {"title": "Updated Sermon Title"}
    result = update_sermon(sermon_id, updated_data)
    assert result

    # Check if the sermon was updated in the collection
    updated_sermon = docs_store_collection.find_one({"sermon_id": sermon_id})
    assert updated_sermon is not None
    assert updated_sermon["title"] == "Updated Sermon Title"


def test_delete_sermon():
    # Upload a test sermon
    sermon_id = upload_sermon(
        title="Test Sermon",
        cover_url="https://example.com/cover.jpg",
        document_url="https://example.com/document.pdf",
        minister="Test Minister",
        description="This is a test sermon.",
    )

    # Delete the sermon
    result = delete_sermon(sermon_id)
    assert result

    # Check if the sermon was deleted from the collection
    deleted_sermon = docs_store_collection.find_one(
        {"sermon_id": sermon_id},
    )
    print(f"Deleted: {deleted_sermon}")
    assert deleted_sermon is None
