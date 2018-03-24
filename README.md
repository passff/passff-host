passff-host
===========

[![Join the chat at https://gitter.im/jvenant/passff](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jvenant/passff?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Host app for the WebExtension **[PassFF](https://addons.mozilla.org/firefox/addon/passff)**

### Overview
This piece of software wraps around the **[zx2c4 pass](http://www.zx2c4.com/projects/password-store/)** shell command. It has to be installed for the PassFF browser extension to work properly.

### Installation
Download the `install_host_app.sh` script from [our releases page](https://github.com/passff/passff-host/releases) and execute it. You can do this in one line like so:

```
$ curl -sSL https://github.com/passff/passff-host/releases/download/1.0/install_host_app.sh | bash -s -- [firefox|chrome|opera|chromium|vivaldi]
```

This script will download the host application (a small python script) and the add-on's manifest file (a JSON config file) and put them in the right place.
If you're concerned about executing a script that downloads files from the web, you can download the files yourself and run the script with the `--local` option instead or link the files yourself. Details below.

#### Windows
Download the `install_host_app.bat` script from [our releases page](https://github.com/passff/passff-host/releases) and execute it from within a shell with a correct PATH.
*The rule of thumb is: if you can execute pass and python from your shell, then your host application will be installed correctly.*

```
> install_host_app.bat [firefox|chrome|opera|chromium|vivaldi]
```

Note: Older Windows versions might require powershell to be installed manually as the install script uses powershell internally. Windows 10 users should be fine out of the box.

#### Latest from GitHub
This is not recommended! Only for developers and for testing purposes!

Clone the repository. Then, from the project's `src/` directory, run `make` and execute the installation script in `bin/testing` for your desired browser (`firefox`, `chrome`, `opera`, `chromium`, or `vivaldi`):

```
$ cd ./src
$ make
$ cd ../bin/testing
$ ./install_host_app.sh --local [firefox|chrome|opera|chromium|vivaldi]
```

This will copy the host application and manifest files to the right place for your browser. The `--local` option makes the script use the files on disk rather than downloading them from GitHub.

If this doesn't work, you can link the files yourself. First, change the `path` value in the `passff.json` file to be the absolute path to the project's `bin/testing/passff.py` file. Then symlink (or copy) the file `bin/testing/passff.json` to the appropriate location for your browser and OS:

- Firefox
  - Linux
    - Per-user: `~/.mozilla/native-messaging-hosts/passff.json`
    - System-wide: `/usr/{lib,lib64,share}/mozilla/native-messaging-hosts/passff.json`
  - OS X
    - `/Library/Application Support/Mozilla/NativeMessagingHosts/passff.json`
  - Windows
    - Per-user: `Path contained in registry key HKEY_CURRENT_USER\Software\Mozilla\NativeMessagingHosts\passff`
    - System-wide: `Path contained in registry key HKEY_LOCAL_MACHINE\SOFTWARE\Mozilla\NativeMessagingHosts\passff`
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

### Preferences
By modifying the `preferences section` in `passff.py` you will be able to set
  - the path to the `pass` script,
  - additional command line arguments that are passed to `pass`,
  - the shell `stdout` charset,
  - additional environment variables.
