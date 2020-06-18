# SCP-079-ID - Get Telegram ID
# Copyright (C) 2019-2020 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-ID.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from subprocess import run, PIPE

from pyrogram import Client, Filters, Message

from .. import glovar
from ..functions.command import command_error, get_command_type
from ..functions.etc import bold, code, get_readable_time, lang, mention_id, thread
from ..functions.filters import from_user, test_group
from ..functions.group import get_group
from ..functions.telegram import resolve_username, send_message

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.group & ~Filters.forwarded & Filters.command(["id"], glovar.prefix)
                   & ~test_group
                   & from_user)
def id_group(client: Client, message: Message) -> bool:
    # Get ID in group
    result = False

    try:
        # Basic data
        gid = message.chat.id
        uid = message.from_user.id
        mid = message.message_id

        # Generate the text
        if message.reply_to_message.from_user:
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_id'))}\n"
                    f"{lang('user_id')}{lang('colon')}{code(uid)}\n"
                    f"{lang('replied_id')}{lang('colon')}{code(message.reply_to_message.from_user.id)}\n"
                    f"{lang('group_id')}{lang('colon')}{code(gid)}\n")

        else:
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_id'))}\n"
                    f"{lang('user_id')}{lang('colon')}{code(uid)}\n"
                    f"{lang('group_id')}{lang('colon')}{code(gid)}\n")

        if not message.chat.restrictions:
            return thread(send_message, (client, gid, text, mid))

        text += (f"{lang('restricted_group')}{lang('colon')}{code('True')}\n"
                 f"{lang('restricted_reason')}{lang('colon')}" + code("-") * 24 + "\n\n")
        text += "\n\n".join(bold(f"{restriction.reason}-{restriction.platform}") + "\n" + code(restriction.text)
                            for restriction in message.chat.restrictions)

        # Send the report message
        thread(send_message, (client, gid, text, mid))

        result = True
    except Exception as e:
        logger.warning(f"ID group error: {e}", exc_info=True)

    return result


@Client.on_message(Filters.incoming & Filters.private & ~Filters.forwarded & Filters.command(["id"], glovar.prefix)
                   & from_user)
def id_private(client: Client, message: Message) -> bool:
    # Get id in private chat by command
    result = False

    try:
        # Basic data
        cid = message.chat.id
        uid = message.from_user.id
        mid = message.message_id

        # Get command type
        command_type = get_command_type(message)

        # Check the command
        if not command_type:
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_id'))}\n"
                    f"{lang('user_id')}{lang('colon')}{code(uid)}\n")
            return thread(send_message, (client, cid, text, mid))

        # Get the id
        the_type, the_id = resolve_username(client, command_type)

        # Check the id
        if not the_type or the_type not in {"channel", "user"} or not the_id:
            return command_error(client, message, lang("action_id"), lang("command_para"), report=False)

        # User
        if the_type == "user":
            text = (f"{lang('action')}{lang('colon')}{code(lang('action_id'))}\n"
                    f"{lang('user_id')}{lang('colon')}{code(the_id)}\n")
            return thread(send_message, (client, cid, text, mid))

        # Channel or group
        text = f"{lang('action')}{lang('colon')}{code(lang('action_id'))}\n"

        chat = get_group(client, the_id)

        if not chat:
            text += f"ID{lang('colon')}{code(the_id)}\n"
            return thread(send_message, (client, cid, text, mid))

        if chat.type == "channel":
            text += f"{lang('channel_id')}{lang('colon')}{code(the_id)}\n"
        elif chat.type == "supergroup":
            text += f"{lang('group_id')}{lang('colon')}{code(the_id)}\n"
        else:
            text += f"ID{lang('colon')}{code(the_id)}\n"

        if not chat.restrictions:
            return thread(send_message, (client, cid, text, mid))

        restrict_type = lang("restricted_channel") if chat.type == "channel" else lang("restricted_group")
        text += (f"{restrict_type}{lang('colon')}{code('True')}\n"
                 f"{lang('restricted_reason')}{lang('colon')}" + code("-") * 24 + "\n\n")
        text += "\n\n".join(bold(f"{restriction.reason}-{restriction.platform}") + "\n" + code(restriction.text)
                            for restriction in chat.restrictions)

        # Send the report message
        thread(send_message, (client, cid, text, mid))

        result = True
    except Exception as e:
        logger.warning(f"ID private error: {e}", exc_info=True)

    return result


@Client.on_message(Filters.incoming & Filters.private & ~Filters.forwarded & Filters.command(["start"], glovar.prefix)
                   & from_user)
def start(client: Client, message: Message) -> bool:
    # Start the bot
    result = False

    try:
        # Basic data
        cid = message.chat.id
        mid = message.message_id

        # Generate the text
        if not glovar.start_text:
            return False

        text = glovar.start_text

        # Send the report message
        thread(send_message, (client, cid, text, mid))

        result = True
    except Exception as e:
        logger.warning(f"Start error: {e}", exc_info=True)

    return result


@Client.on_message(Filters.incoming & Filters.group & Filters.command(["version"], glovar.prefix)
                   & test_group
                   & from_user)
def version(client: Client, message: Message) -> bool:
    # Check the program's version
    result = False

    try:
        # Basic data
        cid = message.chat.id
        aid = message.from_user.id
        mid = message.message_id

        # Get command type
        command_type = get_command_type(message)

        # Check the command type
        if command_type and command_type.upper() != glovar.sender:
            return False

        # Generate the text
        git_hash = run("git rev-parse --short HEAD", stdout=PIPE, shell=True)
        git_hash = git_hash.stdout.decode()
        git_date = run("git log -1 --format='%at' | xargs -I{} date -d @{} +'%Y/%m/%d %H:%M:%S'",
                       stdout=PIPE, shell=True)
        git_date = git_date.stdout.decode()
        command_date = get_readable_time(message.date, "%Y/%m/%d %H:%M:%S")
        text = (f"{lang('admin')}{lang('colon')}{mention_id(aid)}\n\n"
                f"{lang('project')}{lang('colon')}{code(glovar.sender)}\n"
                f"{lang('version')}{lang('colon')}{code(glovar.version)}\n"
                f"{lang('git_hash')}{lang('colon')}{code(git_hash)}\n"
                f"{lang('git_date')}{lang('colon')}{code(git_date)}\n"
                f"{lang('command_date')}{lang('colon')}{code(command_date)}\n")

        # Send the report message
        result = send_message(client, cid, text, mid)
    except Exception as e:
        logger.warning(f"Version error: {e}", exc_info=True)

    return result