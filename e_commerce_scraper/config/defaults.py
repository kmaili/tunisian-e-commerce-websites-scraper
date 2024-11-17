import os
import logging
from sys import platform

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORKING_DIR = os.getcwd()

PLATFORM = platform


output_folder = "."
# selenium
remote = False
use_selenium = True
platform = "win32"
# platform             = 'LINUX'
driver_type = "chrome"
driver_path = os.path.join(BASE_DIR, "libs", platform, "chromedriver")
disable_dev_shm_usage = True
headless = False
# driver_language      = 'fr-FR'
driver_language = "en-EN"
base_url = "https://mytek.tn/"

logging_folder = os.path.join(WORKING_DIR, "logs", "ecommerce.log")
# if not logs folder exists create one
# if not
os.makedirs(os.path.join(WORKING_DIR, "logs"), exist_ok=True)
# : os.makedirs(os.path.join(WORKING_DIR, 'logs'))
logging_level = logging.INFO
logging_format = "%(asctime)s:[%(levelname)s]: [%(lineno)d]: %(message)s"
verbose = True
