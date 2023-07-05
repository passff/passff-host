#!/usr/bin/env python3
"""
    Host application of the browser extension PassFF
    that wraps around the zx2c4 pass script.
"""

import json
import os
import re
import shlex
import struct
import subprocess
import sys

VERSION = "_VERSIONHOLDER_"

###############################################################################
######################## Begin preferences section ############################
###############################################################################
COMMAND = "pass"
COMMAND_ARGS = []
COMMAND_ENV = {
    "TREE_CHARSET": "ISO-8859-1",
    "PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
}
CHARSET = "UTF-8"

###############################################################################
######################### End preferences section #############################
###############################################################################


def getMessage():
    """ Read a message from stdin and decode it. """
    rawLength = sys.stdin.buffer.read(4)
    if len(rawLength) == 0:
        sys.exit(0)
    messageLength = struct.unpack('@I', rawLength)[0]
    message = sys.stdin.buffer.read(messageLength).decode("utf-8")
    return json.loads(message)


def encodeMessage(messageContent):
    """ Encode a message for transmission, given its content. """
    encodedContent = json.dumps(messageContent)
    encodedLength = struct.pack('@I', len(encodedContent))
    return {'length': encodedLength, 'content': encodedContent}


def sendMessage(encodedMessage):
    """ Send an encoded message to stdout. """
    sys.stdout.buffer.write(encodedMessage['length'])
    sys.stdout.write(encodedMessage['content'])
    sys.stdout.flush()


def setPassGpgOpts(env, opts_dict):
    """ Add arguments to PASSWORD_STORE_GPG_OPTS. """
    opts = env.get('PASSWORD_STORE_GPG_OPTS', '')
    for opt, value in opts_dict.items():
        re_opt = new_opt = opt
        if value is not None:
            re_opt = rf"{opt}(?:=|\s+)\S*"
            new_opt = (
                f"{opt}={shlex.quote(value)}"
                if opt.startswith("--") else
                f"{opt} {shlex.quote(value)}"
            )
        # If the user's environment sets this opt, remove it.
        opts = re.sub(re_opt, '', opts)
        opts = f"{new_opt} {opts}"
    env['PASSWORD_STORE_GPG_OPTS'] = opts.strip()


def getGpgCodesFromStderr(stderr):
    preserve = []
    # https://github.com/gpg/libgpg-error/blob/master/src/err-codes.h.in
    error_code = 0
    for line in stderr.split("\n"):
        m = re.search(r'gpg: DBG: chan_\d+ (?:<-|->) ERR (\d+)', line)
        if m is not None:
            error_code = int(m.group(1)) & 0xFFFF
        elif line.startswith("[GNUPG:]"):
            m = re.search(r'ERROR pkdecrypt_failed (\d+)', line)
            if m is not None:
                error_code = int(m.group(1)) & 0xFFFF
            elif 'NO_SECKEY' in line:
                error_code = 17
            elif 'ENC_TO' in line:
                preserve.clear()
            elif 'BEGIN_DECRYPTION' in line:
                preserve = preserve[-1:]
            elif 'END_DECRYPTION' in line:
                break
        elif len(preserve) > 0 and line.startswith('  '):
            # gpg indented line continuation
            preserve[-1] += '\n' + line
        elif not line.startswith('gpg: DBG:'):
            preserve.append(line)
    # Filter out any gpg: DBG: messages that might've slipped through.
    return '\n'.join(preserve), error_code


if __name__ == "__main__":
    # Read message from standard input
    receivedMessage = getMessage()
    opt_args = []
    pos_args = []
    std_input = None

    if len(receivedMessage) == 0:
        opt_args = ["show"]
        pos_args = ["/"]
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
    opt_args += COMMAND_ARGS

    # Set up (modified) command environment
    env = dict(os.environ)
    if "HOME" not in env:
        env["HOME"] = os.path.expanduser('~')
    for key, val in COMMAND_ENV.items():
        env[key] = val
    setPassGpgOpts(env, {'--status-fd': '2', '--debug': 'ipc'})

    # Set up subprocess params
    cmd = [COMMAND] + opt_args + ['--'] + pos_args
    proc_params = {
        'input': bytes(std_input, CHARSET) if std_input else None,
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'env': env
    }

    # Run and communicate with pass script
    proc = subprocess.run(cmd, **proc_params)

    # Send response
    decoded_stderr = proc.stderr.decode(CHARSET)
    stderr, error_code = getGpgCodesFromStderr(decoded_stderr)
    sendMessage(
        encodeMessage({
            "exitCode": proc.returncode,
            "stdout": proc.stdout.decode(CHARSET),
            "stderr": stderr,
            "errorCode": error_code,
            "version": VERSION
        }))
