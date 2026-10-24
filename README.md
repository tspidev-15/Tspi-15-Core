
## Discord Bots (Experimental)

TSPI-15 includes an experimental integration for creating simple
Discord slash commands using `.tspi` files.

### Requirements

- Python 3.10 or newer
- A Discord application and bot token

### Installation

Install TSPI-15 with Discord support:

```bash
python -m pip install -e ".[discord]"
```

### Example

Create a file named `examples/discord_ping.tspi`:

```text
bot "TSPI Bot"

command "ping":
    reply "Pong!"
```

### Run the bot

Set your Discord bot token in an environment variable:

```bash
export DISCORD_TOKEN="YOUR_BOT_TOKEN"
```

Then run:

```bash
tspi15-discord examples/discord_ping.tspi
```

Keep the terminal running while you use the bot.

### Security

Never publish your Discord bot token in GitHub or include it
in a `.tspi` source file.

### Current limitations

This integration currently supports slash commands with fixed text
replies. It does not yet support arbitrary TSPI-15 statements inside
Discord commands, moderation, tickets, or role management.
