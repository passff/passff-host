#!/usr/bin/env python3

"""
    Host application of the browser extension PassFF
    that wraps around the zx2c4 pass script.
"""

import os, sys, json, struct, subprocess

VERSION = "_VERSIONHOLDER_"

################################################################################
######################## Begin preferences section #############################
################################################################################
COMMAND = subprocess.check_output("which pass", shell=True).strip()
COMMAND_ARGS = []
COMMAND_ENV  = {
    "TREE_CHARSET": "ISO-8859-1",
    # Default PATH for MacOS:
    #"PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
}
CHARSET      = "UTF-8"
################################################################################
######################### End preferences section ##############################
################################################################################

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

if __name__ == "__main__":
    # Read message from standard input
    receivedMessage = getMessage()
    opt_args = []
    pos_args = []
    std_input = None

    if len(receivedMessage) == 0:
        pass
    elif receivedMessage[0] == "insert":
        opt_args = ["insert", "-m"]
        pos_args = [receivedMessage[1]]
        std_input = receivedMessage[2]
    elif receivedMessage[0] == "generate":
        pos_args = [receivedMessage[1], receivedMessage[2]]
        opt_args = ["generate"]
        if "-n" in receivedMessage[3:]:
            opt_args.append("-n")
    else:
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
    sendMessage(encodeMessage({
        "exitCode": proc.returncode,
        "stdout": proc.stdout.decode(CHARSET),
        "stderr": proc.stderr.decode(CHARSET),
        "version": VERSION
    }))
