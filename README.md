# CUI-SDK : AudioTranscriptionService

The cooking-up-ideas sdk provides tools to artists for audio-visual projects.

### Getting Started

Future interface:
```
cui-sdk session start --config config.yaml

cui-sdk transcriber upload-to-s3 --input-dir input_wav/

cui-sdk transcriber run-transcriptions --input-dir input_wav/

cui-sdk transcriber dl-transcriptions --input-dir input_wav/ --output-dir transcription_files/
```

This last command will create an output directory in "./transcription_files/", relative to where the command is being run, with the same structure and filename_convention as in input_wav/ ... the filenames will be the same plus "_transcription", and be a .txt file instead of a WAV file.

### Current Interface

#### Setup AWS credentials

ASSUME_ROLE_OUTPUT=$(aws sts assume-role \
    --role-arn arn:aws:iam::671388079324:role/terraform-cooking-up-ideas \
    --role-session-name cooking-up-ideas)

export AWS_ACCESS_KEY_ID=$(echo "$ASSUME_ROLE_OUTPUT" | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo "$ASSUME_ROLE_OUTPUT" | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo "$ASSUME_ROLE_OUTPUT" | jq -r '.Credentials.SessionToken')

#### Run Script
python3 main.py input_wav/ output_transcripts/

### Todo

Implement DynamoDB table to use as a caching mechanism

DynamoDB Items:
* session
* * name
* * expiry
* filename
* * uploaded_to_s3?
* * transcribed?

The config.env file contains:
* session_name=my_session
* session_expiry_days=3
* session_scope=
* * [local - will reference absolute paths to a home directory on disk], or
* * [cloud - path to a s3 bucket bucket holding the data]

