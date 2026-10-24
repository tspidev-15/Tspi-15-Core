
import unittest

from tspi15.discord_bot import (
    DiscordScriptError,
    parse_bot_source,
)


class DiscordBotTests(unittest.TestCase):
    def test_parse_ping(self):
        name, commands = parse_bot_source(
            'bot "TSPI Bot"\n'
            'command "ping":\n'
            '    reply "Pong!"\n'
        )
        self.assertEqual(name, "TSPI Bot")
        self.assertEqual(commands, [("ping", "Pong!")])

    def test_requires_bot(self):
        with self.assertRaises(DiscordScriptError):
            parse_bot_source(
                'command "ping":\n'
                '    reply "Pong!"\n'
            )

    def test_rejects_invalid_command_name(self):
        with self.assertRaises(DiscordScriptError):
            parse_bot_source(
                'bot "TSPI Bot"\n'
                'command "Ping!":\n'
                '    reply "Pong!"\n'
            )


if __name__ == "__main__":
    unittest.main()
