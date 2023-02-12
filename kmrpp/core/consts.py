import os

BASE_URL = "https://parentportal.ormiston.school.nz/api/api.php"
DEFAULT_HEADERS = {
    "User-Agent": "MOYAI Moment",
    "Origin": "file://",
    "X-Requested-With": "nz.co.KAMAR",
}
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
if not os.path.exists(CACHE_DIR):
    os.mkdir(CACHE_DIR)
