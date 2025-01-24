import logging
import logging.config
import os

def setup_logger(name, log_file, console_level = logging.INFO, file_level = logging.DEBUG):    
    """
    Setup the logger configuration.
    
    Returns:
        logger: The logger object.
    """
    logger = logging.getLogger(name)
    logger.setLevel(console_level)
    
    if logger.hasHandlers():
        return logger
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(formatter)
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
    