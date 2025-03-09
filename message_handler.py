from telethon.errors import ChatWriteForbiddenError, ForbiddenError, SlowModeWaitError, MessageDeleteForbiddenError, NotFoundError
import logging
import os
from utils import save_method, sent_methods
from config import forbidden_groups, banned_groups



async def check_last_massage(client, group_id, group_name, caption, alternate_caption, channel):
    # Check the last 5 messages sent by all accounts to this group
    found_matching_message = False
    # Avoid sending if a similar message has already been sent by any account
    try:
        async for msg in client.iter_messages(group_id, limit=5):
            found_matching_message = False
            if msg.text and (caption == msg.text or alternate_caption == msg.text):
               logging.info(f"A similar message was already sent in group {group_name} ({group_id}).")
               found_matching_message = True
               try:
                   # Try to delete the message
                   await client.delete_messages(group_id, msg.id)
                   if not msg:
                       logging.info(f"Deleted the message in group {group_name} (message ID: {msg.id}).")
                       found_matching_message = False
                   else:
                       logging.info(f"can't delete the message in group {group_name} (message ID: {msg.id}).")
               except MessageDeleteForbiddenError:
                   logging.error("You don't have permission to delete this message.")
               break
    except NotFoundError:
        logging.error(f"can't get last messages. skipping group {group_name} ({group_id}).")
        found_matching_message = True
    try:
        async for msg in client.iter_messages(group_id, limit=5, from_user=channel):
            if msg:
                logging.info(f"A message from brandAfraz was already sent in group {group_name} ({group_id}).")
                found_matching_message = True
                try:
                    # Try to delete the message
                    await client.delete_messages(group_id, msg.id)
                    if not msg:
                        logging.info(f"Deleted the message in group {group_name} (message ID: {msg.id}).")
                        found_matching_message = False
                    else:
                        logging.info(f"can't delete the message in group {group_name} (message ID: {msg.id}).")
                except MessageDeleteForbiddenError:
                    logging.error("You don't have permission to delete this message.")
                break
    except NotFoundError:
        logging.error(f"can't get last messages. skipping group {group_name} ({group_id}).")
        found_matching_message = True
    return found_matching_message

#function try to forward messages if got deleted calls send_message
async def forward(client, group_id, group_name, photo_path, caption, alternate_caption, message_id, channel):
    try:
        await client.forward_messages(group_id, message_id, channel)
        logging.info(f"forwarded message to {group_name}.")
        sent_methods[group_id] = 'forward'
        save_method()
    except Exception as e:
        logging.error(f"Failed to forward message to {group_name} due to {type(e).__name__}: {e}. Falling back to send_message.")
        await send_message(client, group_id, group_name, photo_path, caption, alternate_caption)

# Function to send messages
async def send_message(client, group_id, group_name, photo_path, caption, alternate_caption):
    if not os.path.exists(photo_path):
        logging.error(f"Photo file does not exist at path: {photo_path}")
        return
    # Send photo with original caption
    try:
        await send_photo_with_caption(client, group_id, group_name, photo_path, caption)
        sent_methods[group_id] = 'photo_with_caption'
        save_method()
        return
    except (MessageDeleteForbiddenError, ForbiddenError):
        logging.warning(f"Message deleted in group {group_name} ({group_id}) due to forbidden content. Retrying without '@'.")
        # Try sending without '@'
        try:
            await send_photo_with_caption(client, group_id, group_name, photo_path, caption.replace('@', ''))
            sent_methods[group_id] = 'photo_without_username'
            logging.info(f'sent without username group {group_name} ({group_id}).')
            save_method()
            return
        except (MessageDeleteForbiddenError, ForbiddenError):
            logging.warning(f"Message deleted again in group {group_name} ({group_id}). Retrying with alternate caption.")
            # Try sending alternate caption
            try:
                await send_photo_with_caption(client, group_id, group_name, photo_path, alternate_caption)
                sent_methods[group_id] = 'alternate_caption'
                save_method()
                return
            except (MessageDeleteForbiddenError, ForbiddenError):
                try:
                    await client.send_file(group_id, photo_path)
                    logging.info(f'sent photo without caption {group_name} ({group_id}).')
                    sent_methods[group_id] = 'photo_without_caption'
                    save_method()
                except (MessageDeleteForbiddenError, ForbiddenError):
                    logging.warning(f"Message deleted again in group {group_name} ({group_id}). Skipping group.")
                    forbidden_groups.append((group_name, group_id))
                    return

    except ChatWriteForbiddenError:
        logging.warning(f"Photo sending not allowed in group {group_name} ({group_id}). Sending text only.")
        # Send text if photo is not allowed
        try:
            await send_text(client, group_id, group_name, caption)
            sent_methods[group_id] = 'text_with_caption'
            save_method()
            return
        except MessageDeleteForbiddenError:
            logging.warning(f"Text message deleted in group {group_name} ({group_id}) due to forbidden content. Retrying without '@'.")
            try:
                await send_text(client, group_id, group_name, caption.replace('@', ''))
                sent_methods[group_id] = 'text_without_username'
                save_method()
                return
            except MessageDeleteForbiddenError:
                logging.warning(f"Text message deleted again in group {group_name} ({group_id}). Retrying with alternate caption.")
                try:
                    await send_text(client, group_id, group_name, alternate_caption)
                    sent_methods[group_id] = 'alternate_text'
                    save_method()
                    return
                except MessageDeleteForbiddenError:
                    logging.warning(f"Alternate text message deleted in group {group_name} ({group_id}). Skipping group.")
                    forbidden_groups.append((group_name, group_id))
                    return
        except ForbiddenError:
            logging.warning(f"Text sending not allowed in group {group_name} ({group_id}).")
    except SlowModeWaitError as e:
        logging.info(f"Slow mode active in {group_name}. Skipping group.")
        return
    except Exception as e:
        if "banned from sending messages" in str(e):
            logging.error(f"Banned from sending messages in group {group_name} ({group_id}). Adding to banned list.")
            banned_groups.append((group_name, group_id))
            return
        logging.error(f"Unexpected error in group {group_name} ({group_id}): {e}")

async def send_method(sent_method, client, group_id, group_name, photo_path, caption, alternate_caption, message_id, channel):
    try:
        if sent_method == 'photo_without_caption':
            await client.send_file(group_id, photo_path)
        elif sent_method == 'forward':
            await client.forward_messages(group_id, message_id, channel)
        elif sent_method == 'photo_with_caption':
            await send_photo_with_caption(client, group_id, group_name, photo_path, caption)
            logging.info(f'used saved method {sent_method} in group {group_name}')
        elif sent_method == 'text_with_caption':
            await send_text(client, group_id, group_name, caption)
            logging.info(f'used saved method {sent_method} in group {group_name}')
        elif sent_method == 'alternate_caption':
            await send_photo_with_caption(client, group_id, group_name, photo_path, alternate_caption)
            logging.info(f'used saved method {sent_method} in group {group_name}')
        elif sent_method == 'alternate_text':
            await send_text(client, group_id, group_name, alternate_caption)
            logging.info(f'used saved method {sent_method} in group {group_name}')
        elif sent_method == 'text_without_username':
            await send_text(client, group_id, group_name, caption.replace('@', ''))
            logging.info(f'used saved method {sent_method} in group {group_name}')
        elif send_method == 'photo_without_username':
            await send_photo_with_caption(client, group_id, group_name, photo_path, caption.replace('@', ''))
            logging.info(f'used saved method {sent_method} in group {group_name}')
    except MessageDeleteForbiddenError:
        await send_message(client, group_id, group_name, photo_path, caption, alternate_caption)

# Helper functions to send messages
async def send_photo_with_caption(client, group_id, group_name, photo_path, caption):
    await client.send_file(group_id, photo_path, caption=caption)
    logging.info(f"Sent image with caption to group {group_name} ({group_id}).")

async def send_text(client, group_id, group_name, text):
    await client.send_message(group_id, text)
    logging.info(f"Sent text to group {group_name} ({group_id}).")
