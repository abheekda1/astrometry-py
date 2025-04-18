import logging

def setup_logging(level=logging.INFO):
    logging.basicConfig(level=level)
    return logging.getLogger(__name__)

def parse_response(response: dict) -> dict:
    """
    Utility function to clean and parse API responses.
    """
    # TODO: Implement parsing logic (e.g., filter out junk data)
    return response
