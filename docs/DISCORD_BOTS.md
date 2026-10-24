
# Discord bots with TSPI-15

This experimental integration supports slash commands with fixed text replies.

## Install

From the repository root:

    python -m pip install -e ".[discord]"

## Create a bot script

Create `examples/discord_ping.tspi`:

    bot "TSPI Bot"

    command "ping":
        reply "Pong!"

## Configure Discord

1. Visit https://discord.com/developers/applications
2. Create an application and its bot.
3. Copy the bot token privately.
4. Use OAuth2 URL Generator with the `bot` and
   `applications.commands` scopes to invite it to your server.

## Run

Set the token in your terminal, without committing it to GitHub:

    export DISCORD_TOKEN='YOUR_BOT_TOKEN'
    tspi15-discord examples/discord_ping.tspi

Keep the terminal running while using the bot.

## Limitations

This version supports fixed replies only. It does not yet execute
arbitrary TSPI-15 statements inside Discord commands.
Never put your Discord token in a `.tspi` file or on GitHub.
