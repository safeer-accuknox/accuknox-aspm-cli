import logging
import os
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

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

        # Avoid reconfiguring logging if already configured
        if not logger.hasHandlers():
            # Set log level based on environment variable
            logger.setLevel(logging.DEBUG if os.getenv('DEBUG', 'FALSE').upper() == 'TRUE' else logging.INFO)
            
            # Add StreamHandler with colored formatter
            formatter = cls._get_colored_formatter()
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        return logger

    @staticmethod
    def _get_colored_formatter():
        # Custom formatter that adds color to the log level
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                log_message = super().format(record)
                if record.levelname == 'ERROR':
                    return Fore.RED + log_message
                elif record.levelname == 'WARNING':
                    return Fore.YELLOW + log_message  # colorama does not have orange, so using yellow
                elif record.levelname == 'INFO':
                    return Fore.BLUE + log_message
                return log_message
        
        return ColoredFormatter(log_format)
