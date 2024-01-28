from ..models import Sermon
from database.mongodb import docs_store_collection


def upload_sermon(
    title, cover_url, document_url, minister, description=None
):
    sermon = Sermon(
        title=title,
        cover_url=cover_url,
        document_url=document_url,
        minister=minister,
        description=description,
    )

    result = docs_store_collection.insert_one(sermon.dict())
    if result.inserted_id:
        return sermon.sermon_id
    return None


def get_sermon(search_param, search_value):
    search_params = ["sermon_id", "title", "minister"]
    if search_param not in search_params:
        raise ValueError(f'Invalid search param: {search_param}. Allowed params are {search_params}')

    if search_param == "sermon_id":
        result = docs_store_collection.find_one({"sermon_id": search_value})
    else:
        result = docs_store_collection.find_one({search_param: search_value})

    return result


def update_sermon(sermon_id, updated_data):
    result = docs_store_collection.update_one({"sermon_id": sermon_id}, {"$set": updated_data})
    return result.modified_count > 0


def delete_sermon(sermon_id):
    result = docs_store_collection.delete_one({"sermon_id": sermon_id})
    return result.deleted_count > 0
