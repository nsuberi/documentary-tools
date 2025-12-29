from dataclasses import dataclass

@dataclass
class Config:
    # AWS settings
    AWS_REGION = "us-east-1"
    
    # Processing settings
    BATCH_SIZE = 100 # This is b/c of the 100 item limit in DynamoDB batch size

    MAX_CONCURRENT_JOBS = 5
    MAX_RETRIES = 12
    RETRY_DELAY = 5  # seconds
    
    # Audio settings
    TARGET_SAMPLE_RATE = 16000
    TARGET_CHANNELS = 1
    COMPRESSION_QUALITY = 0.7
    
    # Output settings
    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
