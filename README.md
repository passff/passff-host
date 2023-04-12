passff-host
===========

[![Join the chat at https://gitter.im/jvenant/passff](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jvenant/passff?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Host app for the WebExtension **[PassFF](https://addons.mozilla.org/firefox/addon/passff)**

### Overview
This piece of software wraps around the **[zx2c4 pass](http://www.zx2c4.com/projects/password-store/)** shell command. It has to be installed for the PassFF browser extension to work properly.

### Dependencies

#### For the host application
* [`python3`](https://docs.python.org/3.5/) (>= 3.5)
* [`pass`](https://www.passwordstore.org/)

In most cases, a **graphical *pinentry* program** is also needed for use with the PassFF browser extension. For that, please refer to the instructions given in the [PassFF repository](https://github.com/passff/passff#a-graphical-pinentry-program).

#### For the install script (except Windows)
* `curl`
* `sed`

### Installation

#### Linux, MacOS, * BSD

Download the latest `install_host_app.sh` script from [our releases page](https://github.com/passff/passff-host/releases) and execute it. As an example, Firefox users can do this in one line like so:

```bash
curl -sSL github.com/passff/passff-host/releases/latest/download/install_host_app.sh | bash -s -- firefox
```

Users of other supported browsers need to replace the last argument (`firefox`) by `librewolf`, `chrome`, `opera`, `chromium` or `vivaldi`.
The script will download the host application (a small python script) and the add-on's manifest file (a JSON config file) and put them in the right place.
If you're concerned about executing a script that downloads files from the web, you can download the files yourself and run the script with the `--local` option instead or link the files yourself. Details below.

#### Windows
Download the `install_host_app.bat` script from [our releases page](https://github.com/passff/passff-host/releases) and execute it from within a shell with a correct PATH, mentioning your browser in the last argument (i.e., replace `firefox` by `librewolf`, `chrome`, `opera`, `chromium` or `vivaldi` if necessary).
*The rule of thumb is: if you can execute pass and python from your shell, then your host application will be installed correctly.*

```
install_host_app.bat firefox
```

Note: Older Windows versions might require powershell to be installed manually as the install script uses powershell internally. Windows 10 users should be fine out of the box.

#### Latest from GitHub
This is not recommended! Only for developers and for testing purposes!

Clone the repository. Then, run the following command.

```bash
make [VERSION=testing|...] [BROWSER=firefox|librewolf|chrome|opera|chromium|vivaldi] install
```

This will generate the host application and installation scripts for the given `VERSION` (`testing` by default), and copy the host application and manifest files to the right place for your `BROWSER` (`firefox` by default).

This uses the `--local` option of the `install_host_app.sh` script, which instructs it to use the files on disk rather than downloading them from GitHub.

If this doesn't work, you can link the files yourself. First, change the `path` value in the `passff.json` file to be the absolute path to the project's `bin/testing/passff.py` file. Then symlink (or copy) the file `bin/testing/passff.json` to the appropriate location for your browser and OS:

- [Firefox](https://developer.mozilla.org/en-US/Add-ons/WebExtensions/Native_manifests#Manifest_location)
  - Linux
    - Per-user: `~/.mozilla/native-messaging-hosts/passff.json`
    - System-wide: `/usr/{lib,lib64,share}/mozilla/native-messaging-hosts/passff.json`
  - OS X
    - Per-user: `~/Library/Application Support/Mozilla/NativeMessagingHosts/passff.json`
    - System-wide: `/Library/Application Support/Mozilla/NativeMessagingHosts/passff.json`
  - Windows
    - Per-user: `Path contained in registry key HKEY_CURRENT_USER\Software\Mozilla\NativeMessagingHosts\passff`
    - System-wide: `Path contained in registry key HKEY_LOCAL_MACHINE\SOFTWARE\Mozilla\NativeMessagingHosts\passff`
- LibreWolf
  - Linux
    - Per-user: `~/.librewolf/native-messaging-hosts/passff.json`
    - System-wide: `/usr/{lib,lib64,share}/librewolf/native-messaging-hosts/passff.json`
  - OS X
    - Per-user: `~/Library/Application Support/LibreWolf/NativeMessagingHosts/passff.json`
    - System-wide: `/Library/Application Support/LibreWolf/NativeMessagingHosts/passff.json`
  - Windows
    - Per-user: `Path contained in registry key HKEY_CURRENT_USER\Software\LibreWolf\NativeMessagingHosts\passff`
    - System-wide: `Path contained in registry key HKEY_LOCAL_MACHINE\SOFTWARE\LibreWolf\NativeMessagingHosts\passff`
- Chrome
  - Linux
    - Per-user: `~/.config/google-chrome/NativeMessagingHosts/passff.json`
    - System-wide: `/etc/opt/chrome/native-messaging-hosts/passff.json`
  - OS X
    - Per-user: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/passff.json`
    - System-wide: `/Library/Google/Chrome/NativeMessagingHosts/passff.json`
  - Windows
    - Per-user: `HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts\passff`
    - System-wide: `HKEY_LOCAL_MACHINE\SOFTWARE\Google\Chrome\NativeMessagingHosts\passff`
- Chromium
  - Linux
    - Per-user: `~/.config/chromium/NativeMessagingHosts/passff.json`
    - System-wide: `/etc/chromium/native-messaging-hosts/passff.json`
  - OS X
    - Per-user: `~/Library/Application Support/Chromium/NativeMessagingHosts/passff.json`
    - System-wide: `/Library/Application Support/Chromium/NativeMessagingHosts/passff.json`
- Opera
  - Same as Chrome
- Vivaldi
  - Linux
    - Per-user: `~/.config/vivaldi/NativeMessagingHosts/passff.json`
    - System-wide: `/etc/vivaldi/native-messaging-hosts/passff.json`
  - OS X
    - Per-user: `~/Library/Application Support/Vivaldi/NativeMessagingHosts/passff.json`
    - System-wide: `/Library/Application Support/Vivaldi/NativeMessagingHosts/passff.json`

### Troubleshooting

#### Script execution failed
#### Connection to the host app failed or returned an unexpected result

> Connection to the host app failed or returned an unexpected result!
> Make sure you have the latest version of the PassFF host app installed by following the installation instructions on GitHub.

> Script execution failed.

You get one of these error messages? Follow the instructions below!

###### Remove old installations
*Inappropriate installations can override another one that could work. So, it is simpler to remove everything and restart from scratch.*
* Delete any file `passff.json` in the folders `native-messaging-hosts` and `NativeMessagingHosts`
  * For the complete paths of these folders for your OS and browser, see the section above.
* Verify all `passff.json` are deleted by doing a search.
  * Use your best file searching tool. For example: `find / -type f -name 'passff.json'`

###### Reinstall the host application
See the section above.

###### Check that the host application is correctly installed
* Make sure the file `passff.py` is executable
  * `ls -l /path/to/passff.py`
* Open `passff.json` and verify `path` is set to the absolute path of the host executable `passff.py`: for example `"path": "/path/to/passff.py"`

#### PassFF's host application is not working and takes 99% CPU

###### Set a correct PATH in the `passff.py` script
When the PATH variable is not set correctly, `pass` will complain about not finding `getopt` and then loop forever. You can reproduce this behavior on the command line:
```bash
PATH="$(which bash | xargs dirname)" $(which pass)
```

### Advanced Troubleshooting
If nothing above has worked out your issue...

#### Gather information in the web browser
In the preferences of PassFF, you can enable the status bar and debug logs in the Web Console (to open the console: Ctrl+Shift+K in Firefox, Ctrl+Shift+J in Chrome/Chromium). Enable the debugging mode in `about:debugging`, and reload the app.

#### Make sure the version of the host application is supported by PassFF
* Open the `passff.py` file to find its version number
  * `head /path/to/passff.py`

#### Check the output of the host app
* Run `echo -e "\x02\x00\x00\x00[]" | /path/to/passff.py | tail -c +4; echo`
* The typical output for an empty store is:
  * `{"stderr": "", "version": "1.0.1", "exitCode": 0, "stdout": "Password Store\n"}`

#### Check the error code on failure
```console
$ strace -f --trace=execve --string-limit=256 firefox 2>&1 |grep passff
[pid 73124] execve("/home/<USER>/.mozilla/native-messaging-hosts/passff.py", ["/home/<USER>/.mozilla/native-messaging-hosts/passff.py", "/home/<USER>/.mozilla/native-messaging-hosts/passff.json", "passff@invicem.pro"], 0x7fce6a83e500 /* 77 vars */) = -1 EACCES (Permission denied)
```

#### Check the security module configuration
If your browser is confined by a security module such as AppArmor, then its policies might deny the execution of the host application, resulting in syslog entries like this:
```console
$ grep passff /var/log/syslog
Apr 22 19:55:24 <HOST> kernel: [70746.170024] audit: type=1400 audit(1650650124.793:2258): apparmor="DENIED" operation="exec" profile="firefox" name="/home/<USER>/.mozilla/native-messaging-hosts/passff.py" pid=73124 comm=444F4D20576F726B6572 requested_mask="x" denied_mask="x" fsuid=1000 ouid=1000
```

#### Testing OTP support
```console
$ echo -e "\x19\x00\x00\x00[\"otp\",\"/www/github.com\"]" | /path/to/passff.py | tail -c +4; echo
{"exitCode": 0, "stderr": "", "stdout": "123456\n", "version": "1.0.1"}
```

### Preferences
If you use a customized `pass` installation: environment variables, customized repository path or extensions, you may have to customize the *preferences section* in `passff.py`.

By modifying the *preferences section* in `passff.py`, you will be able to set:
  - `COMMAND`: the path to the `pass` script,
  - `COMMAND_ARGS`: additional command line arguments that are passed to `pass`,
  - `COMMAND_ENV`: additional environment variables,
  - `CHARSET`: the shell stdout charset.
