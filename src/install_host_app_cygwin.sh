#!/usr/bin/env sh

# This script is derived from `install.sh` in Danny van Kooten's "browserpass":
# https://github.com/dannyvankooten/browserpass

set -e

usage() {
  echo "Usage: $0 [OPTION] [chrome|chromium|firefox|opera|vivaldi]

  Options:
    -l, --local    Install files from disk instead of downloading them
    -h, --help     Show this message"
}

process_file() {
# $1 source directory
# $2 source URL
# $3 use local
# $4 file name
# $5 regex
# $6 destination path
  if [ "$3" = true ]; then
    cat "$1/$4" | sed -e "$5" > "$6"
  else
    curl -sSL "$2/$4" | sed -e "$5" > "$6"
  fi
}

APP_NAME="passff"
VERSION="_VERSIONHOLDER_"
RELEASE_URL="https://github.com/passff/passff-host/releases/download/$VERSION"
TARGET_DIR=$(cygpath -u "$APPDATA")/$APP_NAME

while [ $# -gt 0 ]; do
  case $1 in
    chrome|chromium|opera|vivaldi)
      BROWSER_NAME=$(echo -n $1 | sed -e "s/^.*$/\u\0/")
      TARGET_REG='HKCU\Software\Google\Chrome\NativeMessagingHosts\'$APP_NAME
      ;;
    firefox)
      BROWSER_NAME="Firefox"
      TARGET_REG='HKCU\Software\Mozilla\NativeMessagingHosts\'$APP_NAME
      ;;
    -l|--local)
      USE_LOCAL_FILES=true
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 1
      ;;
  esac
  shift
done

PYTHON3_PATH="$(readlink -f "$(which python3)")"
if [ -x "$PYTHON3_PATH" ]; then
  echo "Python 3 executable located at $PYTHON3_PATH"
else
  echo "Python 3 executable not found, but Python 3 is required for PassFF to work!"
  exit 1
fi

PASS_PATH="$(which pass)"
if [ -x "$PASS_PATH" ]; then
  echo "Pass executable located at $PASS_PATH"
else
  echo "Pass executable not found, but Pass is required for PassFF to work!"
  exit 1
fi

if [ -z "$TARGET_REG" ]; then
  usage
  exit 1
fi

HOST_FILE_PATH="$TARGET_DIR/$APP_NAME.py"
MANIFEST_FILE_PATH="$TARGET_DIR/$APP_NAME.json"
WRAPPER_FILE_PATH="$TARGET_DIR/${APP_NAME}_cygwin.bat"

echo "Installing $BROWSER_NAME host config"

# Create config dir if not existing
mkdir -p "$TARGET_DIR"

PWD=$(pwd)
process_file "$PWD" "$RELEASE_URL" "$USE_LOCAL_FILES" "$APP_NAME.py" \
  "/^ *\"PATH\":.*$/d" "$HOST_FILE_PATH"
process_file "$PWD" "$RELEASE_URL" "$USE_LOCAL_FILES" "$APP_NAME.json" \
  "s/PLACEHOLDER/$(echo -n "$(cygpath -w "$WRAPPER_FILE_PATH")" | \
    sed -e 's/\\/\\\\\\\\/g')/" \
  "$MANIFEST_FILE_PATH"
CR=$(echo -en "\r")
echo "@ECHO OFF$CR" > "$WRAPPER_FILE_PATH"
echo "SET PATH="\
"$(echo -n $PATH | tr : "\0" | xargs -0 cygpath -w | tr "\n" ";")$CR" >> \
  "$WRAPPER_FILE_PATH"
echo $(cygpath -w "$PYTHON3_PATH") \"$HOST_FILE_PATH\" %%*$CR >> \
  "$WRAPPER_FILE_PATH"
chmod -R 0700 "$TARGET_DIR"

reg ADD "$TARGET_REG" /ve /d "$(cygpath -w "$MANIFEST_FILE_PATH")" /f
