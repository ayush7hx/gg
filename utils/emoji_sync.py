"""Resolve custom emoji markup against the emoji available to this bot.

Emoji IDs are server-independent, but copied embeds often contain stale IDs or
slightly different names.  This module provides a small, safe fallback that
keeps those messages usable in both of the owner's emoji servers.
"""
import re
from difflib import SequenceMatcher
from typing import Dict

EMOJI_MARKUP = re.compile(r"<(?P<animated>a?):(?P<name>[A-Za-z0-9_~+-]+):(?P<id>\d+)>")

EMOJI_FALLBACKS = {
    "arrow": "➡️", "arrowred": "➡️", "safe": "🛡️", "shield": "🛡️",
    "bot": "🤖", "wrench": "🔧", "music": "🎵", "wifi": "📶",
    "sowrd": "⚔️", "sword": "⚔️", "people": "👥", "rocket": "🚀",
    "games": "🎮", "ban": "🚫", "cloud": "☁️", "module": "📁",
    "counting": "🔢", "ai": "🤖", "boost": "🚀", "levelup": "⬆️",
    "pin": "📌", "thunder": "⚡", "lock": "🔒", "mc": "⛏️",
    "msg": "💬", "circle": "⭕", "warning": "⚠️", "timer": "⏱️",
    "staff": "🔨", "play": "▶️", "pause": "⏸️", "mute": "🔇",
    "ticket": "🎟️", "tick": "✅", "settings": "⚙️", "seed": "🌱",
    "plus": "➕", "zplus": "➕", "people": "👥", "delete": "🗑️",
}


def _key(name: str) -> str:
    value = re.sub(r"[^a-z0-9]", "", name.lower()).replace("zyrox", "inf")
    return re.sub(r"^(?:inf|z|icons?)", "", value)


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
            key = _key(match.group("name"))
            candidates = ((candidate_key, candidate) for candidate_key, candidate in index.items())
            best_key, best = max(candidates, key=lambda item: SequenceMatcher(None, key, item[0]).ratio(), default=(None, None))
            if best is not None and SequenceMatcher(None, key, best_key).ratio() >= 0.65:
                emoji = best
        if emoji is None:
            key = _key(match.group("name"))
            return EMOJI_FALLBACKS.get(key, EMOJI_FALLBACKS.get(key.lstrip("z"), "🔹"))
        return str(emoji)

    return EMOJI_MARKUP.sub(replace, content)


def normalize_embed(embed, bot, index=None):
    """Normalize custom emoji markup in every text-bearing Embed property."""
    if embed is None:
        return embed
    index = index or build_emoji_index(bot)
    if embed.title:
        embed.title = normalize_markup(embed.title, bot, index)
    if embed.description:
        embed.description = normalize_markup(embed.description, bot, index)
    if embed.footer and embed.footer.text:
        embed.set_footer(text=normalize_markup(embed.footer.text, bot, index), icon_url=embed.footer.icon_url)
    if embed.author and embed.author.name:
        embed.set_author(name=normalize_markup(embed.author.name, bot, index), url=embed.author.url, icon_url=embed.author.icon_url)
    if embed.fields:
        fields = [
            (normalize_markup(field.name, bot, index), normalize_markup(field.value, bot, index), field.inline)
            for field in embed.fields
        ]
        embed.clear_fields()
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed
