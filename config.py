# Information for multiple accounts
accounts = []

# MTProxy configuration
proxies = []

# List of groups to avoid sending messages
excluded_groups = ['Group A', 'Group B']
forbidden_groups = []
banned_groups = []
sent_methods = {}  # To store how each group was successfully sent a message
TRACKER_FILE = 'sent_method.json'

# Main caption and alternate caption
caption = ''
alternate_caption = ''