from telethon import TelegramClient
from telethon.network.connection.tcpmtproxy import ConnectionTcpMTProxyAbridged
import asyncio
import logging
from message_handler import check_last_massage, forward
from config import banned_groups, forbidden_groups, excluded_groups, caption, alternate_caption, proxies
from utils import get_sent_method


# Choose proxy
def get_proxy():
    return proxies[0]

# Function to get list of groups
async def get_groups(client):
    groups = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            groups.append((dialog.id, dialog.title))
    return groups


# Execute for selected account
async def run_client(account, message_id):
    proxy = get_proxy()
    client = TelegramClient(account['session_name'], account['api_id'], account['api_hash'], connection=ConnectionTcpMTProxyAbridged, proxy=proxy)

    try:
        await client.start(phone=account['phone_number'])
    except Exception as e:
        logging.error(f"Failed to start the client: {e}")
        return

    current_user_id = (await client.get_me()).id
    groups = await get_groups(client)
    photo_path = r""
    channel_name = ''
    channel = await client.get_entity(channel_name)

    for group_id, group_name in groups:
        if group_name in excluded_groups or (group_name, group_id) in banned_groups:
            logging.info(f"Skipping group: {group_name} ({group_id})")
            continue
        flag = await check_last_massage(client, group_id, group_name, caption, alternate_caption, channel)
        if not flag:
            sent_method = get_sent_method(group_id)
            if not sent_method:
                await forward(client, group_id, group_name, photo_path, caption, alternate_caption, message_id, channel)
            else:
                await sent_method(sent_method, client, group_id, group_name, photo_path, caption, alternate_caption, message_id, channel)
        await asyncio.sleep(2)

    for forbidden_group in forbidden_groups:
        logging.info(f"Forbidden group: {forbidden_group}")
    for banned_group in banned_groups:
        logging.info(f"Banned group: {banned_group}")