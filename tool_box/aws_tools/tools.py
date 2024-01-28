import boto3
from botocore.exceptions import BotoCoreError, ClientError


import os
import shutil
import logging


class S3BucketNotFoundError(BotoCoreError):
    """Bucket not found exception class."""
    fmt = 'Could not find bucket - {bucket_name}, or {e}'

    def __init__(self, bucket_name, e ='', **kwargs):
        """Bucket not found exception class."""
        kwargs['bucket_name'] = bucket_name
        kwargs['e'] = e
        super().__init__(**kwargs)


class S3BucketFailToCreateError(BotoCoreError):
    """Bucket failed creation exception class."""
    fmt = 'Failed to create S3 bucket: {reason}'

    def __init__(self, reason, **kwargs):
        """Bucket failed creation exception class."""
        kwargs['reason'] = reason
        super().__init__(**kwargs)


class FolderNotFoundError(BotoCoreError):
    """Folder not found exception class."""
    fmt = 'Failed to find folder with id: {id} in bucket: {bucket_name}'

    def __init__(self, id, bucket_name, **kwargs):
        """Folder not found exception class."""
        kwargs['id'] = id
        kwargs['bucket_name'] = bucket_name
        super().__init__(**kwargs)


class FilesDownloadError(BotoCoreError):
    """Files download error exception class."""
    fmt = 'Failed to download folder with id: {id} in bucket: {bucket_name}'

    def __init__(self, id, bucket_name, **kwargs):
        """Files download error exception class."""
        kwargs['id'] = id
        kwargs['bucket_name'] = bucket_name
        super().__init__(**kwargs)


class BucketUtil():
    '''Class to initialize a bucket utility instance'''
    
    # __BIN is the temporary folder for storing downloaded files
    # Contained within the bin folder, are folders with different
    # ids as folder name. Witin each id are files belonging to that
    # id.
    __BIN = os.path.join(
        os.getcwd(), "document_store"
    )

    def __init__(
        self,
        bucket_name: str,
        force: bool=False,
        region: str="us-east-1"
    ):
        '''
        Validates S3 bucket in a sspecified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        :param bucket_name: Bucket to create
        :param force: if true, creates bucket with bucket_name if bucket does not exist
        :param region: String region to create bucket in, e.g., 'us-west-2'
        '''

        self.bucket_name = bucket_name
        
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=region
        )
        
        # Check that the bucket exists
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            if force:
                # Create a new bucket with bucket_name
                try:
                    # create_bucket_config = {'LocationConstraint': region} if region else {}
                    res = self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        # CreateBucketConfiguration=create_bucket_config
                    )
                    print(res)
                except ClientError as e:
                    raise S3BucketFailToCreateError(
                        reason=f"{e} Could not create bucket {self.bucket_name}"
                    )
            else:
                raise S3BucketNotFoundError(
                    bucket_name=self.bucket_name, e=e
                )

    def list_ids(self):
        '''Return a list all ids in the bucket'''
        
        response = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name, Delimiter='/'
        )
        ids = [
            prefix.get('Prefix')[:-1] for prefix in response.get('CommonPrefixes', [])
        ]
        
        return ids
    
    def list_files_in_folder(self, id):
        """List all files in a specific folder ID.

        :param id: Folder ID to list files from
        :return: List of file names in the folder, or an empty list if the folder is empty or not found
        """
        if id not in self.list_ids():
            raise FolderNotFoundError(id=id, bucket_name=self.bucket_name)

        try:
            # List objects in the bucket with the specified prefix (id)
            objects = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=f"{id}/")

            file_names = [os.path.basename(obj['Key']) for obj in objects.get('Contents', [])]
            return file_names

        except ClientError as e:
            logging.error(e)
            return []
    
    def upload_file(self, id, file_name, file_content):
        """Upload a file to an S3 bucket inside a folder with the specified ID

        :param id: Folder ID to use for organizing the files
        :param file_name: Name to be used for the uploaded file
        :param file_content: Content of the file to upload
        :return: True if file was uploaded, else False
        """

        # Append the folder ID to the object_name to create a folder structure
        object_name = f"{id}/{file_name}"

        try:
            # Use put_object to upload file content directly
            self.s3_client.put_object(Body=file_content, Bucket=self.bucket_name, Key=object_name)
        except ClientError as e:
            logging.error(e)
            return False

        return True

    def delete_file_in_folder(self, id, file_name):
        """Delete a file from a specific folder in the S3 bucket.

        :param id: Folder ID from which to delete the file
        :param file_name: Name of the file to delete
        :return: True if the file was deleted successfully, else False
        """
        if id not in self.list_ids():
            raise FolderNotFoundError(id, self.bucket_name)

        try:
            # Construct the object key using the folder ID and file name
            object_key = f"{id}/{file_name}"

            # Delete the object from the S3 bucket
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)

            return True
        except ClientError as e:
            logging.error(e)
            return False
    
    def download_files(self, id):
        '''Downloads files from s3
        
        :param id: Folder ID to use for organizing the files
        :return: True if file was uploaded, else False
        '''
        if id not in self.list_ids():
            raise FolderNotFoundError(id, self.bucket_name)
        
        storage_path = os.path.join(
            os.getcwd(), self.__BIN, id
        )

        os.makedirs(storage_path, exist_ok=True)

        try:
            # List objects in the bucket with the specified prefix (id)
            objects = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=f"{id}/")

            for obj in objects.get('Contents', []):
                # Extract the object key
                object_key = obj['Key']

                # Extract the file name from the object key
                file_name = os.path.basename(object_key)

                # Download the file
                local_file_path = os.path.join(storage_path, file_name)
                self.s3_client.download_file(self.bucket_name, object_key, local_file_path)

            return True
        except ClientError as e:
            logging.error(e)
            return False

    def delete_from_bin(self, id):
        '''Delete folder with id as name from bin
        
        :param id: Folder ID contaning the files
        :return: True if folder was, else False
        '''
        
        storage_path = os.path.join(
            self.__BIN, id
        )
        
        if not os.path.exists(storage_path):
            return True
        try:
            shutil.rmtree(storage_path, )
            return True
        except OSError as e:
            logging.error(e)
            return False

    def delete_from_bucket(self, id):
        '''Delete folder with id from bucket
        
        :param id: Folder ID contaning the files
        :return: True if folder was, else False
        '''

        if id not in self.list_ids():
            raise FolderNotFoundError(id, self.bucket_name)
        
        try:
            # List objects in the bucket with the specified prefix (id)
            objects = self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=f"{id}/")

            # Extract and delete each object
            objects_to_delete = [{'Key': obj['Key']} for obj in objects.get('Contents', [])]

            if objects_to_delete:
                self.s3_client.delete_objects(Bucket=self.bucket_name, Delete={'Objects': objects_to_delete})
                return True
            else:
                return False

        except ClientError as e:
            logging.error(e)
            return False
    
    def create_upload_presigned_url(
        self,
        id,
        fields=None,
        conditions=None,
        expiration=3600
    ):
        """Generate a presigned URL S3 POST request to upload a file

        :param id: string
        :param fields: Dictionary of prefilled form fields
        :param conditions: List of conditions to include in the policy
        :param expiration: Time in seconds for the presigned URL to remain valid
        :return: Dictionary with the following keys:
            url: URL to post to
            fields: Dictionary of form fields and values to submit with the POST
        :return: None if error.
        
        ### Example:
        ```
        import requests    # To install: pip install requests

        # Generate a presigned S3 POST URL
        util = BucketUtil(
            bucket_name="..."
        )
        response = util.create_upload_presigned_post(id="1")
        if response is None:
            exit(1)

        # Demonstrate how another Python program can use the presigned URL to upload a file
        with open(object_name, 'rb') as f:
            files = {'file': (object_name, f)}
            http_response = requests.post(response['url'], data=response['fields'], files=files)
        # If successful, returns HTTP status code 204
        logging.info(f'File upload HTTP status code: {http_response.status_code}')
        ```
        """
        
        try:
            response = self.s3_client.generate_presigned_post(
                self.bucket_name,
                id,
                Fields=fields,
                Conditions=conditions,
                ExpiresIn=expiration
            )
        except ClientError as e:
            logging.error(e)
            return None

        # The response contains the presigned URL and required fields
        return response
        
        
def main():
    util = BucketUtil(
        bucket_name="petra-document-store"
    )
    print(util.bucket_name)
    folder_id = "test"
    files_in_folder = util.list_files_in_folder(folder_id)
    if files_in_folder:
        print(f"Files in folder {folder_id}: {files_in_folder}")
    else:
        print(f"No files found in folder {folder_id}.")


if __name__ == "__main__":
    main()
