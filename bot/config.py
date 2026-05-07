import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

WORK_START = 9
WORK_END = 20

SLOT_STEP_MINUTES = 30

SERVICE_DURATIONS = {
    "manicure": 90,
    "pedicure": 90,
    "manicure_pedicure": 180,
}
