import logging

logger = logging.getLogger('Pecfest')
logger.setLevel(logging.INFO)

# Add the console handler to the logger
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

# Create a file handler for logging to a .log file
fh = logging.FileHandler('app.log') 
fh.setFormatter(formatter)
logger.addHandler(fh)