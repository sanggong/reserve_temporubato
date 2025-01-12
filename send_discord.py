import datetime
import requests

discord_url = "discord_webhook_url"


def discord_send_message(text):
    message = {"content": f"{str(text)}"}
    requests.post(discord_url, data=message)


if __name__=="__main__":
    discord_send_message("하위")
