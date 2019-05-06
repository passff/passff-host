#!/usr/bin/env python3
"""
    Host application of the browser extension PassFF
    that wraps around the zx2c4 pass script.
"""

import argparse
import json
import os
import struct
import subprocess
import sys

from typing import Any, Dict, List

VERSION = "_VERSIONHOLDER_"

###############################################################################
######################## Begin preferences section ############################
###############################################################################

# The command to use when invoking pass.
PASS_COMMAND = "pass"

# Any additional arguments to unconditionally use when invoking PASS_COMMAND.
PASS_COMMAND_ARGS = []

# Any additional environment variables to set when invoking PASS_COMMAND.
DEFAULT_COMMAND_ENV = {}

# The default stdin/stdout charset (if none can be auto-detected).
DEFAULT_CHARSET = "UTF-8"

###############################################################################
######################### End preferences section #############################
###############################################################################


def detect_charset() -> str:
    """Attempt to automatically detect the charset, or return DEFAULT_CHARSET if
    none could be auto-detected.
    """
    # If the user has LANG or LC_ALL set to a string like "en_us.UTF8", try to
    # use that as the default charset.
    for langvar in ['LANG', 'LC_ALL']:
        envval = os.environ.get('langvar', '')
        if '.' in envval:
            return envval.split('.', 1)[1]

    # If no charset could be auto-detected using the previous method (e.g.
    # LANG=C, or LANG/LC_ALL were not set) then use DEFAULT_CHARSET.
    return DEFAULT_CHARSET


def getMessage() -> Any:
    """ Read a message from stdin and decode it. """
    rawLength = sys.stdin.buffer.read(4)
    if len(rawLength) == 0:
        sys.exit(0)
    messageLength = struct.unpack('@I', rawLength)[0]
    message = sys.stdin.buffer.read(messageLength).decode("utf-8")
    return json.loads(message)


def encodeMessage(messageContent) -> Dict[str, Any]:
    """ Encode a message for transmission, given its content. """
    encodedContent = json.dumps(messageContent)
    encodedLength = struct.pack('@I', len(encodedContent))
    return {'length': encodedLength, 'content': encodedContent}


def sendMessage(encodedMessage) -> None:
    """ Send an encoded message to stdout. """
    sys.stdout.buffer.write(encodedMessage['length'])
    sys.stdout.write(encodedMessage['content'])
    sys.stdout.flush()


def invoke_pass(pass_command: str,
                command_args: List[str],
                command_env: Dict[str, str],
                charset: str) -> None:
    """Invoke the pass command and communicate with it using stdin/stdout."""
    # Read message from standard input
    receivedMessage = getMessage()
    opt_args = []
    pos_args = []
    std_input = None

    if len(receivedMessage) == 0:
        opt_args = ["show"]
    elif receivedMessage[0] == "insert":
        opt_args = ["insert", "-m"]
        pos_args = [receivedMessage[1]]
        std_input = receivedMessage[2]
    elif receivedMessage[0] == "generate":
        opt_args = ["generate"]
        pos_args = [receivedMessage[1], receivedMessage[2]]
        if "-n" in receivedMessage[3:]:
            opt_args.append("-n")
    elif receivedMessage[0] == "grepMetaUrls" and len(receivedMessage) == 2:
        opt_args = ["grep", "-iE"]
        url_field_names = receivedMessage[1]
        pos_args = ["^({}):".format('|'.join(url_field_names))]
    elif receivedMessage[0] == "otp" and len(receivedMessage) == 2:
        opt_args = ["otp"]
        key = receivedMessage[1]
        key = "/" + (key[1:] if key[0] == "/" else key)
        pos_args = [key]
    else:
        opt_args = ["show"]
        key = receivedMessage[0]
        key = "/" + (key[1:] if key[0] == "/" else key)
        pos_args = [key]
    opt_args += command_args

    # Set up (modified) command environment
    env = dict(os.environ)
    if "HOME" not in env:
        env["HOME"] = os.path.expanduser('~')
    for key, val in command_env.items():
        env[key] = val

    # Set up subprocess params
    cmd = [pass_command] + opt_args + ['--'] + pos_args
    proc_params = {
        'input': bytes(std_input, charset) if std_input else None,
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'env': env
    }

    # Run and communicate with pass script
    proc = subprocess.run(cmd, **proc_params)

    # Send response
    sendMessage(
        encodeMessage({
            "exitCode": proc.returncode,
            "stdout": proc.stdout.decode(charset),
            "stderr": proc.stderr.decode(charset),
            "version": VERSION
        }))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-V', '--version', action='store_true',
                        help='Print passff-host version')
    parser.add_argument('-c', '--pass-command', default=PASS_COMMAND,
                        help='Executable to use as the "pass" command')
    parser.add_argument('-E', '--env', action='append',
                        help='Additional env vars to use in pass process '
                        'environment, supplied in format KEY=VAL')
    parser.add_argument('--charset', default=detect_charset(),
                        help='Charset to use for stdin/stdout communication')
    args = parser.parse_args()

    # If the -V or --version flag was used, just print the passff-host version
    # and exit.
    if args.version:
        print(VERSION)
        return

    # Unconditionally add PASS_COMMAND_ARGS to the pass command, and also add
    # any additional positional arguments from the argument parser.
    command_args = PASS_COMMAND_ARGS + args.args

    # Update DEFAULT_COMMAND_ENV with any env vars supplied by the -E or --env
    # flags. These should be in the format of key=val, for example:
    #
    #   passff.py -E foo=val
    #
    # Could be used to force foo=val in the pass environment.
    command_env = DEFAULT_COMMAND_ENV.copy()
    for env_keyval in args.env:
        key, val = env_keyval.split('=', 1)
        command_env[key] = val

    # Invoke the pass command
    invoke_pass(args.pass_command, command_args, command_env, args.charset)


if __name__ == '__main__':
    main()
