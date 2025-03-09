from telethon import TelegramClient
from telethon.network.connection.tcpmtproxy import ConnectionTcpMTProxyAbridged
import sys
import logging
import asyncio


accounts = []

groups = []

proxies = []


def get_proxy():
    import random
    return random.choice(proxies)


def choose_account():
    print("Select the account to use:")
    for i, account in enumerate(accounts):
        print(f"{i + 1}. {account['session_name']}")

    choice = int(input("Enter the number of the account: ")) - 1
    if 0 <= choice < len(accounts):
        return accounts[choice]
    else:
        print("Invalid choice. Please try again.")
        return choose_account()


logging.basicConfig(
    level=logging.INFO,  # Set the minimum logging level
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format of the logs
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler('my_log_file.log', encoding='utf-8')]
)


async def send_massage():
    account = choose_account()
    client = TelegramClient(account['session_name'], account['api_id'], account['api_hash'], connection=ConnectionTcpMTProxyAbridged , proxy=get_proxy())
    await client.start()

    # Replace with your channel username or ID
    channel_name = ''
    # Replace with your target group name or ID
    target_group = ''
    # The specific message you want to forward (e.g., message ID)

    # Fetch the channel entity
    channel = await client.get_entity(channel_name)

    # Fetch the message from the channel
    message_id = 000

    # Get the group entity
    group = await client.get_entity(target_group)

    # Get all members of the group
    async for user in client.iter_participants(group):
        try:
            # Forward the message to the user
            await client.forward_messages(user.id, message_id, channel)
            logging.info(f'Message forwarded to {user.first_name} - {user.id}')
        except Exception as e:
            logging.error(f'Failed to forward message to {user.id}: {e}')



async def main():
    await send_massage()

if __name__ == "__main__":
    asyncio.run(main())