# tasks.py
import os
from celery import Celery
from celery import shared_task
import requests
from subtitle_search_engine.settings import BASE_DIR
from video_process.models import Video
from subtitle_search_engine.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_REGION_NAME
import boto3
import logging
import subprocess
from datetime import datetime
import re
# import pdb
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'subtitle_search_engine.settings')

# Create a Celery instance and configure it using the settings from Django.
app = Celery('subtitle_search_engine')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps.
app.autodiscover_tasks()

def download_video(video_url, output_file_path):
    # Make the HTTP request
    with requests.get(video_url, stream=True) as response:
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open a file for writing in binary mode
            with open(output_file_path, 'wb') as output_file:
                # Iterate over the content in chunks and write to the file

                output_file.write(response.content)
            print(f"Downloaded video to {output_file_path}")
        else:
            print(f"Failed to download video. Status code: {response.status_code}")

# Example usage


def extract_captions(input_video, output_file):
    # CCExtractor command
    ccextractor_command = [
        'ccextractor',
        input_video,
        '-o', output_file
    ]
    # Run CCExtractor as a subprocess
    try:
        subprocess.run(ccextractor_command, check=True)
        print(f"Closed captions extracted successfully and saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error extracting closed captions: {e}")

import re

def parse_srt(srt_content):
    result = []
    srt_content=convert_to_uppercase(srt_content)

    # Split the SRT content into individual subtitle entries
    subtitle_entries = re.split(r'\n\d+\n', srt_content.strip())

    for entry in subtitle_entries:
        # Extract the timecodes and subtitles using regex
        match = re.match(r'(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\n(.+)', entry, re.DOTALL)

        if match:
            t1, t2, subs = match.groups()
            # Remove extra spaces, newline characters, and '<' from subtitles
            subs = re.sub(r'\s+', ' ', subs.strip())
            subs = subs.replace('<', '')
            result.append({
                "segment": [t1, t2],
                "subs": subs
            })

    return result

def read_srt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        srt_content = file.read()
    return srt_content



def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"Error deleting file '{file_path}': {e}")

def check_substring(a, b):
    # Check if a is a substring of b
    if a in b:
        return 1
    
    # Check if a substring of a is in b
    for i in range(len(a)):
        for j in range(i + 1, len(a) + 1):
            substring = a[i:j]
            if substring in b:
                return 2
    
    
    return 0

# Example usage
def longest_common_substring(str1, str2):
    len_str1 = len(str1)
    len_str2 = len(str2)

    # Create a 2D matrix to store the length of common substrings
    dp = [[0] * (len_str2 + 1) for _ in range(len_str1 + 1)]

    # Variables to store the length and end position of the longest common substring
    max_length = 0
    end_position = 0

    for i in range(1, len_str1 + 1):
        for j in range(1, len_str2 + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1

                if dp[i][j] > max_length:
                    max_length = dp[i][j]
                    end_position = i
            else:
                dp[i][j] = 0

    # Extract the longest common substring
    common_substring = str1[end_position - max_length:end_position]

    return common_substring

def check_substring(a, b):
    # Check if a is a substring of b
    if a in b:
        return 1

    # Check if a substring of a is in b
    for i in range(len(a)):
        for j in range(i + 1, len(a) + 1):
            substring = a[i:j]
            if substring in b:
                return 2

    return 0


# Example usage
def longest_common_substring(str1, str2):
    len_str1 = len(str1)
    len_str2 = len(str2)

    # Create a 2D matrix to store the length of common substrings
    dp = [[0] * (len_str2 + 1) for _ in range(len_str1 + 1)]

    # Variables to store the length and end position of the longest common substring
    max_length = 0
    end_position = 0

    for i in range(1, len_str1 + 1):
        for j in range(1, len_str2 + 1):
            if str1[i - 1] == str2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1

                if dp[i][j] > max_length:
                    max_length = dp[i][j]
                    end_position = i
            else:
                dp[i][j] = 0

    # Extract the longest common substring
    common_substring = str1[end_position - max_length : end_position]
    return common_substring


def remove_extra_spaces(input_string):
    # Use regular expression to replace multiple spaces with a single space
    cleaned_string = re.sub(r'\s+', ' ', input_string)
    return cleaned_string.strip()

def convert_to_uppercase(input_string):
    return ''.join(char.upper() if char.islower() else char for char in input_string)



@shared_task(queue='VideoQueue')                          
def perform_search(id, phrase):
   
    ins = Video.get(id)
    print(type(ins))
    
    if not ins.exists():
        return["please put a valid video ID"]
    if ins.status != "processed":
        return ["Video is not processed yet please try again in few seconds"]
    phrase=remove_extra_spaces(phrase)
    phrase=convert_to_uppercase(phrase)
    print(phrase)
    subarr = ins.subtitles
    times = []
    for i in range(len(subarr)):
        obj = subarr[i]
        a = check_substring(phrase, obj["subs"])
        if a == 1:
            time = []
            time.append(obj["segment"][0])
            time.append(obj["segment"][1])
            times.append(time)
        # You might want to add more conditions for a == 2 here
        if a == 2:
            time = []
            time.append(obj["segment"][0])
            sub3 = longest_common_substring(phrase, obj["subs"])
          #  print("1" + " " + sub3)
            flag = "g"
            count = i
            while i + 1 < len(subarr):
                sub2 = longest_common_substring(subarr[i + 1]["subs"], phrase)
                if sub2 == "":
                    i = count + 1
                    flag = "r"
                    break
                if sub2 != "":
                    sub3 = sub3 + " " + sub2
                    sub3 = remove_extra_spaces(sub3)
                 #   print("2" + " " + sub3)
                    if sub3 == phrase:
                        time.append(subarr[i + 1]["segment"][1])
                        flag = "r"
                        i = count + 1
                        break
                    if flag == "r":
                        break
                    if sub3 in phrase:
                        i = i + 1
                    if sub3 not in phrase:
                      #  print(sub3 + " " + "sdcwedcedc")
                        flag = "r"
                        i = count + 1
                        break
                    if flag == "r":
                        break
                if flag == "r":
                    break

            time.sort()
           # print(time)
            if len(time) == 2:
                times.append(time)
    return times
@shared_task(queue='VideoQueue')
def process_video(id):
    print("Here is the message:", id)
   # Video.objects.filter(id=id).update(status="processing")
    
    ins = Video.get(id)
    # pdb.set_trace()
    
    print(ins)
    ins.status = "processing"
    video_url = ins.download_url
    output_path = f"{BASE_DIR}/videos/{id}.mp4"
    print(output_path)
    
    try:
        download_video(video_url, output_path)
        print("Downloaded video")
    except Exception as e:
        print(e)
    try:
        s3 = boto3.client('s3', aws_access_key_id= AWS_ACCESS_KEY_ID, aws_secret_access_key= AWS_SECRET_ACCESS_KEY, region_name= AWS_S3_REGION_NAME)
        s3.upload_file(output_path, AWS_STORAGE_BUCKET_NAME, f"videos/{id}.mp4")
        ins.s3path = f"https://backendproject1.s3.ap-south-1.amazonaws.com/videos/{id}.mp4"
        print("Uploaded to S3")
    except Exception as e:
       print(e)
    extract_captions(output_path, f"{BASE_DIR}/subs/{id}.srt")
    print("Extracted captions")
    srt_content = read_srt_file(f"{BASE_DIR}/subs/{id}.srt")
    print("Read SRT file")
    subs = parse_srt(srt_content)

    print("Parsed SRT file")
  #  print(subs)
    ins.subtitles = subs
    ins.status = "processed"
    ins.save()
    print("Saved to DB")
    delete_file(output_path)
    print("Deleted video file")
   # delete_file(f"{BASE_DIR}/subs/{id}.srt")
    print("Deleted SRT file")
    return id







