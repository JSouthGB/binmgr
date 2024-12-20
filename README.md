# bingmgr
___
A tool to download and install binaries from GitHub releases. This script is originally the result of
Truenas not allowing packages to be installed. I then figured it would be useful for all the random
VMs and containers I spin up.

## How it works
___
The script will download the latest version of each binary and install it to `$HOME/.local/bin/`. It keeps
track of the currently installed version in the same directory. If you want to check for updates, just run
the script again. When updates are found, they will be downloaded and installed and the versions file
will be updated to reflect the new version.

## Notes
___
The `requests` package is required to run the script. I haven't tested it with a wide variety of programs,
just the ones in the example configuration file below.

## Installation
___
You can either clone the repo and use the script directly or install it as a binary.

## Configuration
___
The configuration file is JSON and needs to be located either in the same directory as the script/
binary file name `binmgr_config.json` or located at `$HOME/.config/binmgr/config.json`.

You can also specify a configuration file using the `--config` option.

```bash
bingmgr --config /a/path/to/my_config.json
```

Example configuration file:
```json
{
  "programs": {
    "bat": "sharkdp/bat",
    "duf": "muesli/duf",
    "eza": "eza-community/eza",
    "gdu": "dundee/gdu",
    "rclone": "rclone/rclone",
    "lazydocker": "jesseduffield/lazydocker"
  }
}
```
The format is `{"program_name": "github_username/repo_name"}`.

## Usage
___
If you're using it as a script, run it as `python3 main.py`. If you're using it as a binary, run it
as `./bingmgr`. Or you can install it to your system using `sudo install -Dm 755 bingmgr /usr/bin/bingmgr`
and run it as `bingmgr`. Or you can install it wherever you want and setup an alias. Just make sure it's executable,
`chmod +x binmgr`.
