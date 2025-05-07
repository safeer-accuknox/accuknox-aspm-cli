import logging
import os

class Logger:
    _instance = None
    
    @classmethod
    def get_logger(cls):
        if not cls._instance:
            cls._instance = cls._initialize_logger()
        return cls._instance
    
    @classmethod
    def _initialize_logger(cls):
        logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        logger.setLevel(logging.DEBUG if os.getenv('DEBUG', 'FALSE').upper() == 'TRUE' else logging.INFO)
        return logger