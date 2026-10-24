
"""Experimental Discord slash-command runner for TSPI-15."""

import json
import os
import re
import sys
from pathlib import Path


class DiscordScriptError(ValueError):
    """Invalid Discord script."""


def parse_bot_source(source):
    bot_name = None
    commands = []
    current_name = None
    current_reply = None

    def finish_command(line_number):
        nonlocal current_name, current_reply
        if current_name is not None:
            if current_reply is None:
                raise DiscordScriptError(
                    f"Line {line_number}: command needs an indented reply."
                )
            commands.append((current_name, current_reply))
            current_name = None
            current_reply = None

    for number, raw in enumerate(source.splitlines(), 1):
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue

        indent = len(raw) - len(raw.lstrip(" "))
        text = raw.strip()

        if indent == 0:
            finish_command(number)

            match = re.fullmatch(r'bot\s+("(?:\\.|[^"\\])*")', text)
            if match:
                if bot_name is not None:
                    raise DiscordScriptError(
                        f"Line {number}: only one bot declaration is allowed."
                    )
                bot_name = json.loads(match.group(1))
                if not bot_name.strip():
                    raise DiscordScriptError("Bot name cannot be empty.")
                continue

            match = re.fullmatch(
                r'command\s+("(?:\\.|[^"\\])*")\s*:', text
            )
            if match:
                if bot_name is None:
                    raise DiscordScriptError(
                        'Declare bot "Name" before commands.'
                    )
                name = json.loads(match.group(1))
                if not re.fullmatch(r"[a-z0-9_-]{1,32}", name):
                    raise DiscordScriptError(
                        "Command names must use lowercase letters, "
                        "numbers, _ or - (1–32 characters)."
                    )
                if any(existing == name for existing, _ in commands):
                    raise DiscordScriptError(
                        f"Duplicate command: {name}"
                    )
                current_name = name
                current_reply = None
                continue

            raise DiscordScriptError(
                f"Line {number}: expected bot or command declaration."
            )

        if indent != 4 or current_name is None:
            raise DiscordScriptError(
                f"Line {number}: use four spaces inside a command."
            )
        if current_reply is not None:
            raise DiscordScriptError(
                f"Line {number}: only one reply is supported per command."
            )

        match = re.fullmatch(
            r'reply\s+("(?:\\.|[^"\\])*")', text
        )
        if not match:
            raise DiscordScriptError(
                f'Line {number}: expected reply "message".'
            )
        current_reply = json.loads(match.group(1))

    finish_command(len(source.splitlines()) + 1)

    if bot_name is None:
        raise DiscordScriptError('Missing bot "Name" declaration.')
    if not commands:
        raise DiscordScriptError("Add at least one command.")

    return bot_name, commands


def run_bot(bot_name, commands, token):
    try:
        import discord
        from discord import app_commands
    except ImportError as exc:
        raise RuntimeError(
            'Install Discord support with: '
            'python -m pip install -e ".[discord]"'
        ) from exc

    client = discord.Client(intents=discord.Intents.default())
    tree = app_commands.CommandTree(client)

    for name, reply_text in commands:
        async def callback(
            interaction: discord.Interaction,
            message=reply_text,
        ):
            await interaction.response.send_message(message)

        tree.add_command(
            app_commands.Command(
                name=name,
                description=f"TSPI-15 command {name}",
                callback=callback,
            )
        )

    @client.event
    async def on_ready():
        try:
            synced = await tree.sync()
            print(f"Connected as {client.user}")
            print(f"Registered {len(synced)} slash command(s).")
        except Exception as exc:
            print(f"Command registration failed: {exc}", file=sys.stderr)

    print(f"Starting TSPI-15 bot: {bot_name}")
    client.run(token)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Run a Discord bot script written in TSPI-15."
    )
    parser.add_argument("file", help="Path to the .tspi bot file")
    args = parser.parse_args()

    try:
        source = Path(args.file).read_text(encoding="utf-8")
        bot_name, commands = parse_bot_source(source)
    except (OSError, DiscordScriptError, json.JSONDecodeError) as exc:
        print(f"tspi15-discord: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print(
            "Set DISCORD_TOKEN in your environment. "
            "Never put your token in a source file.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    try:
        run_bot(bot_name, commands, token)
    except RuntimeError as exc:
        print(f"tspi15-discord: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
