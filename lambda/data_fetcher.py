import json
import logging
import sys
import requests
import io
import pandas as pd
import datetime
import boto3
from decouple import config

# Configure logging (compatible with Lambda and local testing)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3 = boto3.client('s3')

# Only add handler if not already present (Lambda adds its own)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def handler(event, context):
    """
    Lambda function handler to fetch data from an external API.
    
    Args:
        event: Lambda event data
        context: Lambda runtime context
        
    Returns:
        Response with status code and body containing result or error message
        
    Raises:
        Exception: On validation errors or processing failures
    """
    logger.info("Starting data fetch from API")
    
    try:
        api_url = config("API_URL", default=None)
        requests_timeout = int(config("REQUESTS_TIMEOUT", default="0"))
        bucket_name = config("BUCKET_NAME")
        
        # Validate configuration
        if not api_url:
            msg = "API_URL environment variable is not configured."
            logger.error(msg)
            raise ValueError(msg)
        
        if requests_timeout == 0:
            msg = "REQUESTS_TIMEOUT environment variable is not configured."
            logger.error(msg)
            raise ValueError(msg)
        
        if not bucket_name:
            msg = "BUCKET_NAME environment variable is not configured."
            logger.error(msg)
            raise ValueError(msg)
        
        # ----------------- Data extraction -----------------
        #  Fetch data from the API
        logger.info(f"Fetching data from {api_url}")
        
        response = requests.get(api_url, timeout=requests_timeout)
        response.raise_for_status()
        data = response.json()        
        logger.info("Data fetched successfully")
        
        data_users = data.get("results", [])
        row_count = len(data_users)
        logger.info(f"Number of records fetched: {row_count}")
        
        # ----------------- Data Transformation -----------------
        # Process data and write to Parquet
        df = pd.json_normalize(data_users)
        logger.info("Listing columns with their respective data types")
        logger.info(df.dtypes)
        
        # Clean up data types: keep numeric types and convert only object columns to string
        logger.info("Cleaning data types for Parquet conversion...")
        
        # Columns that should remain as numeric types
        numeric_columns = {
            'location.street.number': 'int64',
            'location.postcode': 'int64',
            'dob.age': 'int64',
            'registered.age': 'int64',
        }
        
        for col in df.columns:
            if col in numeric_columns:
                # Keep numeric columns as their type - convert None/NaN to 0
                target_type = numeric_columns[col]
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(target_type)
                logger.info(f"Column '{col}' kept as {target_type}")
            elif df[col].dtype == 'object':
                # Convert only object columns to string to handle mixed types
                df[col] = df[col].astype(str)
                logger.info(f"Column '{col}' converted to string")
            else:
                # Keep other numeric types as they are
                logger.info(f"Column '{col}' kept as {df[col].dtype}")
        
        # ----------------- Data Loading -----------------
        # Use BytesIO to write Parquet in memory before uploading to S3
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, engine='pyarrow', index=False)

        # Define the S3 key (path) with Hive-style partitioning
        # year=YYYY/month=MM/day=DD/file_UUID.parquet
        now = datetime.datetime.now()
        s3_key = (
            f"raw/users/"
            f"year={now.year}/month={now.month:02}/day={now.day:02}/" # Use the execution ID as the filename
        )

        parquet_buffer.seek(0)
        s3.put_object(Bucket=bucket_name, Key=s3_key, Body=parquet_buffer.getvalue())
        logger.info(f"Parquet file uploaded to S3: {bucket_name}/{s3_key}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Data extracted and saved to S3 successfully.",
                "s3_path": f"s3://{bucket_name}/{s3_key}",
                "users_count": row_count
            }),
        }
    
    except requests.exceptions.Timeout as e:
        msg = "Request timeout while fetching data from API"
        logger.error(msg)
        raise TimeoutError(msg) from e
    
    except requests.exceptions.RequestException as e:
        msg = f"Error fetching data from API: {str(e)}"
        logger.error(msg)
        raise RuntimeError(msg) from e
    
    except json.JSONDecodeError as e:
        msg = f"Invalid JSON response from API: {str(e)}"
        logger.error(msg)
        raise ValueError(msg) from e
    
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, exc_info=True)
        raise Exception(msg)
    