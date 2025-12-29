import boto3
import asyncio
from typing import Dict
from botocore.exceptions import ClientError
from config import Config
import random

class AWSTranscribeClient:
    def __init__(self):
        self.client = boto3.client('transcribe', region_name=Config.AWS_REGION)
        self.s3_client = boto3.client('s3', region_name=Config.AWS_REGION)

    async def start_transcription_job(self, job_name: str, file_uri: str) -> Dict:
        """Start an AWS Transcribe job."""
        try:
            response = await asyncio.to_thread(
                self.client.start_transcription_job,
                TranscriptionJobName=f"{job_name}_{str(random.random()).replace('.', '')}",
                Media={'MediaFileUri': file_uri},
                MediaFormat='wav',
                LanguageCode='es-US',
                Settings={
                    'ShowSpeakerLabels': True,
                    'MaxSpeakerLabels': 10
                }
            )
            return response
        except ClientError as e:
            raise Exception(f"Failed to start transcription job: {str(e)}")

    async def get_transcription_result(self, job_name: str) -> Dict:
        """Get the results of a transcription job."""
        attempt = None
        try:
            for _ in range(Config.MAX_RETRIES):
                attempt = _
                response = await asyncio.to_thread(
                    self.client.get_transcription_job,
                    TranscriptionJobName=job_name
                )
                
                status = response['TranscriptionJob']['TranscriptionJobStatus']
                
                if status == 'COMPLETED':
                    print(f'Num of retries until completion: {attempt}')
                    print(response)
                    return response['TranscriptionJob']['Transcript']
                elif status == 'FAILED':
                    raise Exception(f"Transcription job failed: {response['TranscriptionJob']['FailureReason']}")
                
                await asyncio.sleep(Config.RETRY_DELAY)

            raise Exception("Transcription job timed out")
        except ClientError as e:
            print(f'Num of retries until failure: {attempt}')
            raise Exception(f"Failed to get transcription result: {str(e)}")

    async def upload_to_s3(self, file_path: str, bucket: str, key: str) -> str:
        """Upload file to S3 and return the URI."""
        try:
            await asyncio.to_thread(
                self.s3_client.upload_file,
                file_path,
                bucket,
                key
            )
            return f"s3://{bucket}/{key}"
        except ClientError as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
