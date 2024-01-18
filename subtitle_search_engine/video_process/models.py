from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, ListAttribute
from subtitle_search_engine.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME
class Video(Model):
    # Define attributes with specific DynamoDB types
    class Meta:
        table_name = 'videos'
        aws_access_key_id = AWS_ACCESS_KEY_ID
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY
        region = AWS_S3_REGION_NAME

    # Use NumberAttribute for auto-incrementing integer ID
    id = UnicodeAttribute(hash_key=True, null=False)
    subtitles = ListAttribute(null=True)
    download_url = UnicodeAttribute(null=True)
    s3path = UnicodeAttribute(null=True)
    status = UnicodeAttribute(null=True)
