from django.shortcuts import render
from .models import Video
import uuid
from video_process.tasks import process_video
from subtitle_search_engine.settings import BASE_DIR
from video_process.tasks import perform_search
import requests
from pynamodb.exceptions import DoesNotExist
def is_video_link(url):
    try:
        response = requests.head(url, allow_redirects=True)
        content_type = response.headers.get('content-type', '').lower()

        # Check if the content type indicates a video file
        video_content_types = ['video/', 'application/octet-stream']
        for video_type in video_content_types:
            if video_type in content_type:
                return True

        return False

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return False

def uploadVideo(request):
    if request.method == 'POST':
        video_link = request.POST.get('video_link')
        if not is_video_link(video_link):
            return render(request, 'uploadVideo.html', {'error_message': "please put a valid link to the video"})
        print(video_link)
        ins = Video(id=str(uuid.uuid4()), download_url=video_link, s3path="", subtitles="", status="pending")
        ins.save()
        ins2= Video.get(ins.id)
        print(ins2.download_url+ " jkdcwsdocc" )
        print(ins.id)
        print(BASE_DIR)
        try:
            process_video.apply_async(args=[ins.id])
            return render(request, 'upload_success.html', {'id': ins.id})
        except Exception as e:
              
            return render(request, 'uploadVideo.html', {'error_message': f"please put a valid link to the video{e}"})

    return render(request, 'uploadVideo.html')

def searchPhrases(request):
    if request.method == 'POST':
        video_id = request.POST.get('video_id')

        search_phrase = request.POST.get('search_phrase')
        try:
            ins=Video.get(video_id)

        # Check if video_id and search_phrase are not None or empty
            if video_id and search_phrase:
                # Handle the search logic using video_id and search_phrase...
    
                # For example, you might want to pass search results to the template
                search_results = perform_search(video_id, search_phrase)
                return render(request, 'search_phrases_result.html', {'results': search_results})
            else:
                return render(request, 'search_phrases.html', {'error_message': "please put valid video id and phrase"})
        except DoesNotExist:
    # Video with the given ID does not exist
    # Handle this case, maybe return an error or perform some other action
            
            print(f"Video with ID {id} does not exist.")
            return render(request, 'search_phrases.html', {'error_message': "please put valid video id"})


    return render(request, 'search_phrases.html')

def homePage(request):
    return render(request, 'home_page.html')

def query_all_id_s3path():
    videos = Video.scan()
    id_s3path_list = [(video.id, video.s3path) for video in videos]

    return id_s3path_list

def listVideos(request):
    id_s3path_list = query_all_id_s3path()
    return render(request, 'video_list.html', {'id_s3path_list': id_s3path_list})