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
# Default command for MacOS:
#command = "/usr/local/bin/pass"
command     = "/usr/bin/pass"
commandArgs = []
commandEnv  = {
    "TREE_CHARSET": "ISO-8859-1",
    # Default PATH for MacOS:
    #"PATH": "/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
}
charset     = "UTF-8"
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
    stdin = None

    if len(receivedMessage) == 0:
        pass
    elif receivedMessage[0] == "insert":
        opt_args = ["insert", "-m"]
        pos_args = [receivedMessage[1]]
        stdin = receivedMessage[2]
    elif receivedMessage[0] == "generate":
        pos_args = [receivedMessage[1], receivedMessage[2]]
        opt_args = ["generate"]
        if "-n" in receivedMessage[3:]:
            opt_args.append("-n")
    else:
        key = receivedMessage[0]
        key = "/" + (key[1:] if key[0] == "/" else key)
        pos_args = [key]
    opt_args += commandArgs

    # Set up (modified) command environment
    env = dict(os.environ)
    if "HOME" not in env:
        env["HOME"] = os.path.expanduser('~')
    for key, val in commandEnv.items():
        env[key] = val

    # Set up subprocess params
    cmd = [command] + opt_args + ['--'] + pos_args
    proc_params = {
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'env': env
    }
    if 'stdin' is not None:
      proc_params['stdin'] = subprocess.PIPE

    # Run and communicate with pass script
    proc = subprocess.Popen(cmd, **proc_params)
    if stdin is not None:
      proc_in = bytes(stdin, charset)
      proc_out, proc_err = proc.communicate(input=proc_in)
    else:
      proc_out, proc_err = proc.communicate()

    # Send response
    sendMessage(encodeMessage({
        "exitCode": proc.returncode,
        "stdout": proc_out.decode(charset),
        "stderr": proc_err.decode(charset),
        "version": VERSION
    }))
