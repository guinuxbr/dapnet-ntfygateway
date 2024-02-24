# Installing `dapnet-ntfygateway`

## Installation

*You should only ever need to do this once - unless you totally b0rk it!*

You'll need SSH access to your MMDVM node. Start off by making sure you have the correct software installed to run this script:

If you use Ubuntu or another Debian based Linux distribution:

```shell
sudo apt update && sudo apt upgrade
```

```shell
sudo apt install git python3 python3-venv
```

It's likely you'll already have `python3` installed, but it doesn't hurt to check.  It's also kinda necessary.

Now download and set up the environment for the tool:

Create the folder for the script and download it:

```shell
mkdir -p ~/git
```

```shell
cd ~/git
```

```shell
git clone https://github.com/thelovebug/dapnet-ntfygateway
```

```shell
cd dapnet-ntfygateway
```

Set up the environment to run it and download dependencies:

```shell
python3 -m venv venv
```

```shell
source ./venv/bin/activate
```

```shell
pip install -r requirements.txt
```

Create the folder to store the logs.

```shell
mkdir -p ~/logs/dapnet-ntfygateway
```

There, all installed.  Next thing is to prep your config file.

Copy the sample config into the live location:

```shell
cp config.json.example config.json
```

Now edit your `config.json` file in your favourite text editor.  The bits to change are self-explanatory, but here's a guide:

```json
"profiles": {
    "anyname": {                            # change anyname to something that helps you identify this profile - your DMR ID perhaps?
        "ric": "your-ric",                  # change your-ric to the RIC provided by DAPNET, it's usually a variation on your DMR ID
        "call": "your-callsign",            # change your-callsign to - guess what? - your callsign, case isn't important
        "endpoint": "your-ntfy-endpoint",   # change your-ntfy-endpoint, it'll start with https://ntfy.sh/ - check that website for info
        "enabled": true,                    # everything else can stay as is for now
        "alertoncall": true,
        "messagetypes": [
            "M",
            "E",
            "I",
            "D"
        ]
    }
}
```

You're ready to go!

## Configuring the script as a service

To make the script start at boot and to keep it running in the background, we will use a `Systemd` service.

Ensure the correct folder to host `Systemd` user services exists.

```shell
mkdir -p ~/.config/systemd/user/
```

Copy the service file to the right location.

``` shell
cp dapnet-ntfygateway.service ~/.config/systemd/user/
```

Ensure the service file have the correct permissions.

``` shell
chmod 644 ~/.config/systemd/user/dapnet-ntfygateway.service
```

Make `Systemd` aware of the new service file.

```shell
systemctl --user daemon-reload
```

Start the service.

```shell
systemctl --user start dapnet-ntfygateway.service
```

Enable the service.

```shell
systemctl --user enable dapnet-ntfygateway.service
```

Good luck, and reach out to me (via [QRZ](https://qrz.com/db/M7TLB)) if you have any issues.
