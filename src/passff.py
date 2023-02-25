# coding: utf-8

#!/usr/bin/env python3
"""
    Host application of the browser extension PassFF
    that wraps around the zx2c4 pass script.
"""

import json
import os
import struct
import sys
import passpy
import re

VERSION = "2.0.0"

###############################################################################
######################## Begin preferences section ############################
###############################################################################
GPG_BIN = "C:\\Program Files (x86)\\GnuPG\\bin\\gpg.exe"
GIT_BIN = None
STORE_DIR = "C:\\Users\\username\\password-store"
USE_AGENT = False
###############################################################################
######################### End preferences section #############################
###############################################################################
# Message constants
MSG_STORE_NOT_INITIALISED_ERROR = ('You need to call {0} init first.'
                                   .format(__name__))
MSG_PERMISSION_ERROR = 'Nah-ah!'
MSG_FILE_NOT_FOUND = 'Error: {0} is not in the password store.'
MSG_RECURSIVE_COPY_MOVE_ERROR = 'Error: Can\'t {0} a directory into itself.'
MSG_NOT_IMPLEMENTED = 'Error: {0} is not implemented.'

# Tree Constants
SPACES = '    '
BRIDGE = '│   '
BRANCH = '├── '
ENDING = '└── '
    
store = passpy.Store(gpg_bin = GPG_BIN, git_bin = GIT_BIN, store_dir = STORE_DIR, use_agent = USE_AGENT, interactive = False, verbose = False)

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
    
def _gen_tree(lines):
    """Create hierarchical file tree from key names.

    :param list lines: A list of key names from the password store.

    :rtype: dict
    :returns: A nested dictionary with directories and key names as
        it's keys.

    """
    tree = {}
    for line in lines:
        ctree = tree
        for segment in line.split(os.sep):
            if segment not in ctree:
                ctree[segment] = {}
            ctree = ctree[segment]

    return tree

def _print_tree(tree, seperators=None):
    """Print a depth indented listing.

    The algorithm for printing the tree has been taken from `doctree`_
    written by Mihai Ciumeicaă and licensed under the MIT licence.  The
    code has been adapted to fit our needs.

    .. _doctree: https://github.com/cmihai/docktree

    :param dict tree: A dictionary created by
        :func:`passpy.__main__._gen_tree`.

    :param list seperators: (optional) The seperators to print before
       the leaf name.  Leave empty when calling this function.

    """
    if seperators is None:
        seperators = []

    tree_out = ''
    
    length = len(tree)
    for i, entry in enumerate(sorted(tree, key=str.lower)):
        for seperator in seperators:
            if seperator:
                tree_out += BRIDGE
            else:
                tree_out += SPACES
        if i < length - 1:
            tree_out += BRANCH
            tree_out += entry + "\n"
            tree_out += _print_tree(tree[entry], seperators + [1])
        else:
            tree_out += ENDING
            tree_out += entry + "\n"
            tree_out += _print_tree(tree[entry], seperators + [0])

    return tree_out

if __name__ == "__main__":
    # Read message from standard input
    receivedMessage = getMessage()
        
    outCode = 0
    outMessage = None
    outError = None

    if len(receivedMessage) == 0:
        try:
            keys = list(store.iter_dir('.'))
        except StoreNotInitialisedError:
            outError = MSG_STORE_NOT_INITIALISED_ERROR
            outCode = 1
        except FileNotFoundError:
            outError = MSG_FILE_NOT_FOUND.format(subfolder)
            outCode = 1
            
        tree = _gen_tree(keys)
        outMessage = _print_tree(tree)
    elif receivedMessage[0] == "insert":
        force = receivedMessage[1]
        data = receivedMessage[2]
        store.set_key(pass_name, data, force=force)
    elif receivedMessage[0] == "generate":
        pass_name = receivedMessage[1]
        pass_length = receivedMessage[2]
        symbols = True
        if "-n" in receivedMessage[3:]:
            symbols = False
        force = False
        in_place = False

        try:
            password = store.gen_key(pass_name, pass_length, symbols, force, in_place)
        except StoreNotInitialisedError:
            outError = MSG_STORE_NOT_INITIALISED_ERROR
            outCode = 1
        except PermissionError:
            outError = MSG_PERMISSION_ERROR
            outCode = 1
        except FileNotFoundError:
            outError = MSG_FILE_NOT_FOUND.format(pass_name)
            outCode = 1

        if password is None:
            outCode = 1

        outMessage = 'The generated password for {0} is:'.format(pass_name) + "\n" + password
    elif receivedMessage[0] == "grepMetaUrls" and len(receivedMessage) == 2:
        url_field_names = receivedMessage[1]
        searchTerm = "^({}):".format('|'.join(url_field_names))

        try:
            results = store.search(searchTerm)
        except passpy.StoreNotInitialisedError:
            outError = MSG_STORE_NOT_INITIALISED_ERROR
            outCode = 1

        outMessage = ''

        for key in results:
            outMessage += key.replace("\\", '/') + ':' + "\n"
            
            for line, match in results[key]:
                start = match.start()
                end = match.end()
                
                line[:start]
                outMessage += line[:start]
                if re.match(r"^\s*$", line[:start]) != None:
                    outMessage + "\n"
                outMessage += line[start:end]
                outMessage += line[end:] + "\n"
    elif receivedMessage[0] == "otp" and len(receivedMessage) == 2:
        outCode = 1
        outError = MSG_NOT_IMPLEMENTED.format('OTP')
    else:
        key = receivedMessage[0]
        if key[0] == "/":
            del key[0] 
        
        try:
            data = store.get_key(pass_name)
        except StoreNotInitialisedError:
            outError = MSG_STORE_NOT_INITIALISED_ERROR
            outCode = 1
        except FileNotFoundError:
            outError = MSG_FILE_NOT_FOUND.format(pass_name)
            outcode = 1
        except PermissionError:
            outError = MSG_PERMISSION_ERROR
            outCode = 1

        outMessage = data

    # Send the message
    sendMessage(
        encodeMessage({
            "exitCode": outCode,
            "stdout": outMessage,
            "stderr": outError,
            "version": VERSION
        })
    )