import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry(max_retries=3, delay=1, backoff=2):
    """Decorator to add retry logic with exponential backoff."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.warning(f"Attempt {retries + 1} failed: {e}")
                    if retries == max_retries - 1:
                        logger.error(f"Max retries ({max_retries}) exceeded. Last error: {e}")
                        raise
                    time.sleep(delay * (backoff ** retries))
                    retries += 1
            return None
        return wrapper
    return decorator

# Example usage:
@retry(max_retries=5, delay=2, backoff=1.5)
def fetch_data_from_api():
    """Simulate an API call that may fail."""
    import random
    if random.random() < 0.7:
        raise Exception("API call failed")
    return "Data fetched successfully"

if __name__ == "__main__":
    try:
        result = fetch_data_from_api()
        print(result)
    except Exception as e:
        print(f"Error: {e}")