"""This module holds functions to handle the messages"""

import re
import time

import requests


def extract_message(message_text: str, settings: dict) -> dict:
    """This takes a raw line from the DAPNETGateway logfile that we're
    currently monitoring, and if it recognises is as one of the message
    types we're looking for, extracts the pertinent data into a more
    structured format via the message dictionary, which is returned.

    Args:
        message_text (str): _the raw logfile entry text to be parsed_
        settings (dict): _the settings dictionary_

    Returns:
        dict: _a dictionary containing the message and associated metadata determined by this function_
    """

    # Checking for Message
    pattern = re.compile(settings["regex"]["message"])
    matches = pattern.findall(message_text)

    message = {}
    message["type"] = "X"

    if matches:

        message["type"] = "M"
        message["date"] = matches[0][0]
        message["ric"] = matches[0][1]
        message["text"] = matches[0][2]

        message["subject"] = "Message via DAPNET"
        message["body"] = message["text"]
        message["tags"] = f'spiral_notepad, dapnet, message, ric-{message["ric"]}, v2'
        message["priority"] = 3

    # Checking for Error
    pattern = re.compile(settings["regex"]["error"])
    matches = pattern.findall(message_text)

    if matches:

        message["type"] = "E"
        message["date"] = matches[0][0]
        message["ric"] = "0000000"
        message["text"] = matches[0][1]

        message["subject"] = "ERROR FROM DAPNET"
        message["body"] = f'[{message["date"]}] {message["text"]}'
        message["tags"] = "rotating_light, dapnet, error, urgent, v2"
        message["priority"] = 5

    # Checking for Debug
    pattern = re.compile(settings["regex"]["debug"])
    matches = pattern.findall(message_text)

    if matches:

        message["type"] = "D"
        message["date"] = matches[0][0]
        message["ric"] = matches[0][1]
        message["text"] = matches[0][2]

        message["subject"] = "Debug via DAPNET"
        message["body"] = message["text"]
        message["tags"] = f'gear, dapnet, debug, ric-{message["ric"]}, v2'
        message["priority"] = 1

    return message


def send_to_ntfy(message: dict, endpoint: str) -> None:
    """Send the message, defined in the message dictionary, to the ntf.sh service.

    Args:
        message (dict): _the message dictionary created by extract_message()_
        endpoint (str): _the ntfy.sh endpoint that the message should be delivered to_
    """

    ntfy_headers = {}

    ntfy_headers["Tags"] = message["tags"]
    ntfy_headers["Priority"] = str(message["priority"])
    ntfy_headers["Title"] = message["subject"]

    response = requests.post(
        endpoint, data=message["body"], headers=ntfy_headers, timeout=10
    )

    response_text = str(response.status_code)

    # Gonna wait a second so we don't end up with multiple messages racing each other
    time.sleep(1)

    print(f"[{response_text}]")


def info_message(infotype: str, settings: dict, **kwargs) -> None:
    """A special function for crafting informational messages.
    These are static, and defined by the infotype parameter.

    Args:
        infotype (str): _a static string to determine which informational message to send_
        settings (dict): _the settings dictionary_
    """

    logfile = kwargs.get("optional", None)

    message = {}

    message["ric"] = "0000000"
    message["text"] = ""
    message["type"] = "I"
    send = False

    if infotype == "online":

        message["subject"] = "DAPNET ntfy pager online"
        message["body"] = "Monitoring for DAPNET calls"
        message["tags"] = "wave, ntfy, online, v2"
        message["priority"] = 3
        send = True

    elif infotype == "logfile_waiting":

        message["subject"] = "Waiting for logfile"
        message["body"] = logfile
        message["tags"] = "hourglass, ntfy, logfile, v2"
        message["priority"] = 1
        send = True

    elif infotype == "logfile_monitoring":

        message["subject"] = "Monitoring logfile"
        message["body"] = logfile
        message["tags"] = "floppy_disk, ntfy, logfile, v2"
        message["priority"] = 1
        send = True

    else:

        print("invalid infotype")

    if send:
        send_message(message, settings)


def send_message(message: dict, settings: dict) -> None:
    """This function prepares the message for sending, and applies
    a series of rules to determine whether the message should be
    sent out of not.  If it deems that it should, it does!

    Args:
        message (dict): _the message dictionary created by extract_message()_
        settings (dict): _the settings dictionary_
    """

    print(message)

    for profile in settings["profiles"]:

        is_addressable_to_target_profile = False
        is_target_profile_enabled = False

        # The rules here are a little complex, but to determine whether a message can potentially be sent to a given user:
        #  a. the type needs to contained within the enabled message types within the profile, AND any of:
        #    x. the target RIC is same as that in the profile, or
        #    y. the text contains the same callsign as that in the profile, or
        #    z. the message type is I (information) or E (error)
        if message["type"] in settings["profiles"][profile]["messagetypes"]:

            if (
                message["ric"] == settings["profiles"][profile]["ric"]
                or (
                    message["text"]
                    .upper()
                    .find(settings["profiles"][profile]["call"].upper())
                    >= 0
                    and settings["profiles"][profile]["alertoncall"]
                    and message["ric"] != "0000008"
                )
                or message["type"] in ["I", "E"]
            ):
                is_addressable_to_target_profile = True

        # The rule here is much simpler: is the profile that we want to send to actually enabled?
        if settings["profiles"][profile]["enabled"]:
            is_target_profile_enabled = True

        # If the message is ready to be sent AND the target profile is enabled, then send the message!
        if (
            is_addressable_to_target_profile is True
            and is_target_profile_enabled is True
        ):
            print(settings["profiles"][profile])
            send_to_ntfy(message, settings["profiles"][profile]["endpoint"])
