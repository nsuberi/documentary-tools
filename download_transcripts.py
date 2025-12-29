import boto3
import requests
import os

def list_and_download_all_transcripts(output_dir="transcripts"):
    """
    List all Amazon Transcribe jobs in the account, and download their transcripts
    to a specified output directory (defaults to 'transcripts' if not provided).
    """

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    transcribe_client = boto3.client('transcribe')
    
    # Collect all transcription jobs using pagination
    all_jobs = []
    response = transcribe_client.list_transcription_jobs(MaxResults=100)
    all_jobs.extend(response.get('TranscriptionJobSummaries', []))
    
    while "NextToken" in response:
        response = transcribe_client.list_transcription_jobs(
            MaxResults=100,
            NextToken=response["NextToken"]
        )
        all_jobs.extend(response.get('TranscriptionJobSummaries', []))
    
    # Iterate over each transcription job and download its transcript
    for job_summary in all_jobs:
        job_name = job_summary["TranscriptionJobName"]
        job_details = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        
        # Get the transcript file URI
        transcript_uri = job_details["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
        
        # Download the transcript data
        print(f"Downloading transcript for job: {job_name}")
        response = requests.get(transcript_uri)
        
        # Save to a local JSON file named after the job
        local_file = os.path.join(output_dir, f"{job_name}.json")
        with open(local_file, "wb") as f:
            f.write(response.content)
        
        print(f"Saved transcript to: {local_file}")

if __name__ == "__main__":
    list_and_download_all_transcripts()
