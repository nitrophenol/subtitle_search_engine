# Subtitle Search Engine

Subtitle Search Engine is a Django-based web application that enables users to upload videos, process them in the background, and search for specific phrases within the video subtitles. The application utilizes the ccextractor binary for subtitle extraction, ensuring accurate and efficient keyword indexing. Processed videos are stored in Amazon S3, and subtitle information is stored in DynamoDB. The backend processing is optimized for low-latency HTTP requests, with a maximum latency of approximately 1 second.

## Features

1. **Subtitle Extraction:**
   - Utilizes ccextractor binary for extracting subtitles from uploaded videos.

2. **Processing and Storage:**
   - Processes videos in the background using Celery workers.
   - Stores processed videos in S3 and subtitles in DynamoDB.

3. **Low-Latency HTTP Requests:**
   - Ensures a maximum latency of approximately 1 second for HTTP requests.

4. **User Workflow:**
   - Workflow involves providing a video link, queuing for processing, and retrieving processed video information.

5. **Subtitle Segmentation:**
   - Subtitles are parsed into segments, each with a time range and associated subtitle text.

6. **Search Functionality:**
   - Users can search for specific words or phrases to retrieve corresponding time segments within the video.

7. **Video List Page:**
   - Displays a list of processed videos with links to S3 and their respective video IDs.

## Workflow Example

```python
# Celery task for video processing
@celery.task
def process_video(video_link):
    # Background tasks include uploading to S3, subtitle extraction, and parsing
    # Save processed subtitles to the database
    # ...

# Search functionality
def search_video(video_id, search_phrase):
    # Retrieve time stamps for the specified search phrase within video subtitles
    # ...

# Video list page
def get_video_list():
    # Retrieve and display a list of processed videos with links to S3 and video IDs
    # ...

## Tech Stack

- **Django:** Web framework for building robust web applications.
- **Celery:** Distributed task queue system for handling background tasks.
- **DynamoDB:** NoSQL database service for scalable and high-performance applications.
- **RabbitMQ:** Message broker for managing communication between components.
- **Redis:** In-memory data store for caching and speeding up data access.

