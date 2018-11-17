import discord
import re
import shlex
import subprocess

import config


def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[
                   :-1]  # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def is_empty_message(message):
    return message in ['\n', '\r\n']


async def do_ping_rule(message, client):
    ping_prefix = 'ping '
    command = message.content

    if not command.startswith(ping_prefix):
        return False

    remaining_str = command[len(ping_prefix):]
    if not is_valid_hostname(remaining_str):  # Print an error
        response = 'the ping request could not find host {}' \
            .format(shlex.quote(remaining_str))
        await client.send_message(message.channel, response)
    else:
        job = 'ping -c 5 {}'.format(shlex.quote(remaining_str))
        process = subprocess.Popen(
            job, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        process.wait()
        output = process.communicate()[0]
        await client.send_message(message.channel, output)

    return True


def main():
    client = discord.Client()

    @client.event
    async def on_message(message):
        if message.author == client.user:  # If user is the bot itself, ignore
            return
        await do_ping_rule(message, client)

    client.run(config.TOKEN)


if __name__ == '__main__':
    main()
