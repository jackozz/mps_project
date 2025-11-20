import json
import logging
import os
import sys
import requests
from decouple import config

# Configure logging (compatible with Lambda and local testing)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
    """
    logger.info("Starting data fetch from API")
    
    try:
        api_url = config("API_URL", default=None)
        requests_timeout = int(config("REQUESTS_TIMEOUT", default=None))
        
        # Validate configuration
        if not api_url:
            msg = "API_URL environment variable is not configured."
            logger.error(msg)
            return _error_response(500, msg)
        
        if requests_timeout is None:
            msg = "REQUESTS_TIMEOUT environment variable is not configured."
            logger.error(msg)
            return _error_response(500, msg)
        
        # ----------------- Fetch data from the API -----------------
        logger.info(f"Fetching data from {api_url}")
        response = requests.get(api_url, timeout=requests_timeout)
        response.raise_for_status()
        data = response.json()
        
        logger.info("Data fetched successfully")
        
        data_users = data.get("results", [])
        row_count = len(data_users)
        logger.info(f"Number of records fetched: {row_count}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Data extracted successfully.",
                "users_count": row_count
            }),
        }
    
    except requests.exceptions.Timeout:
        msg = "Request timeout while fetching data from API"
        logger.error(msg)
        return _error_response(504, msg)
    
    except requests.exceptions.RequestException as e:
        msg = f"Error fetching data from API: {str(e)}"
        logger.error(msg)
        return _error_response(500, msg)
    
    except json.JSONDecodeError as e:
        msg = f"Invalid JSON response from API: {str(e)}"
        logger.error(msg)
        return _error_response(502, msg)
    
    except Exception as e:
        msg = f"Unexpected error: {str(e)}"
        logger.error(msg, exc_info=True)
        return _error_response(500, msg)


def _error_response(status_code: int, message: str):
    """Helper function to format error responses."""
    return {
        "statusCode": status_code,
        "body": json.dumps({"error": message}),
    }

# Local testing
if __name__ == "__main__":
    # Local testing    
    class MockContext:
        pass
    
    logger.info("Running local test...")
    result = handler({}, MockContext())
    print("\n" + "=" * 50)
    print("Response:")
    print("=" * 50)
    print(json.dumps(result, indent=2))