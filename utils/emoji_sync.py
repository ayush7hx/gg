"""Resolve custom emoji markup against the emoji available to this bot.

Emoji IDs are server-independent, but copied embeds often contain stale IDs or
slightly different names.  This module provides a small, safe fallback that
keeps those messages usable in both of the owner's emoji servers.
"""
import re
from typing import Dict

EMOJI_MARKUP = re.compile(r"<(?P<animated>a?):(?P<name>[A-Za-z0-9_~+-]+):(?P<id>\d+)>")


def _key(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower()).replace("zyrox", "inf")


def build_emoji_index(bot) -> Dict[str, object]:
    index: Dict[str, object] = {}
    for guild in bot.guilds:
        for emoji in guild.emojis:
            index.setdefault(_key(emoji.name), emoji)
    return index


def normalize_markup(content: str, bot, index: Dict[str, object] | None = None) -> str:
    """Replace unavailable custom emoji IDs with a matching local emoji."""
    if not content:
        return content
    index = index or build_emoji_index(bot)

    def replace(match):
        emoji = bot.get_emoji(int(match.group("id")))
        if emoji is None:
            emoji = index.get(_key(match.group("name")))
        if emoji is None:
            return match.group(0)
        return str(emoji)

    return EMOJI_MARKUP.sub(replace, content)
