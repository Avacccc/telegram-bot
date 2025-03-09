import logging
import os
import json
from config import TRACKER_FILE
import sys

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler('telegram_log.log', encoding='utf-8')]
)

# Global dictionary to store user IDs of all accounts
account_user_ids = {}

def save_method():
    with open(TRACKER_FILE, 'w') as h:
        json.dump(sent_methods, h)

# Load the message tracker from file
if os.path.exists(TRACKER_FILE):
    with open(TRACKER_FILE, 'r') as f:
        sent_methods = json.load(f)


def get_sent_method(group_id):
    # Check if the group has a recorded method
    global sent_methods
    if os.path.exists('sent_methods.json'):
        with open('sent_methods.json', 'r') as f:
            sent_methods = json.load(f)
    else:
        sent_methods = {}
    if group_id in sent_methods:
        return sent_methods[group_id]
    else:
        return None