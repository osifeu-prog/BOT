import logging
import sys

# הגדרת פורמט לוגים מקצועי: זמן | רמה | הודעה
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("VIP_BOT")
