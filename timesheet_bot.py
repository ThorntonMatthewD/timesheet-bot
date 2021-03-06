import os
import calendar
import datetime

from dotenv import find_dotenv, load_dotenv
from discord_webhook import DiscordWebhook
from discord_webhook.webhook import DiscordEmbed

load_dotenv(find_dotenv(), verbose=True)

DISCORD_WEBHOOK_URL = os.environ.get("webhook")
ROLE_TO_PING = os.environ.get("ping_id")

# BAH Holidays for 2022
HOLIDAYS = [
    "05/30/2022",
    "06/20/2022",
    "07/04/2022",
    "09/05/2022",
    "10/10/2022",
    "11/24/2022",
    "12/26/2022",
]

# Gets the last working day before the 15th and end of a month.
# Has to account for weekends and holidays..
def check_if_sign_date():
    now = datetime.datetime.now()

    if now.day > 15:
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        target_date = datetime.datetime(now.year, now.month, days_in_month)
    else:
        target_date = datetime.datetime(now.year, now.month, 15)

    next_sign_date = get_next_sign_date(target_date)

    return True if next_sign_date.date() == now.date() else False


def get_next_sign_date(target_date):

    not_found = True
    days_offset = 0

    while not_found:
        date_to_examine = target_date + datetime.timedelta(days=days_offset)

        # check if weekday
        if date_to_examine.isoweekday() < 6:
            if check_if_holiday(date_to_examine):
                days_offset -= 1
            else:
                not_found = False
        else:
            days_offset -= 1

    return target_date + datetime.timedelta(days=days_offset)


def check_if_holiday(date):
    for h in HOLIDAYS:
        dt = datetime.datetime.strptime(h, "%m/%d/%Y")

        if dt == date:
            return True

    return False


def send_discord_webhook():
    embed = DiscordEmbed(
        title="It's TIME to Submit Your Timesheet!",
        color="01807e",
        description=f"Don't forget to sign your timesheet in Deltek today!",
    )
    embed.set_timestamp()
    embed.add_embed_field(
        name="Log in now!", value="https://time.bah.com", inline=False
    )
    embed.set_thumbnail(
        url="https://i.kym-cdn.com/photos/images/original/001/879/961/056.gif"
    )
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, rate_limit_retry=True)
    webhook.add_embed(embed=embed)
    webhook.execute()

    webhook = DiscordWebhook(
        url=DISCORD_WEBHOOK_URL, rate_limit_retry=True, content=ROLE_TO_PING
    )
    webhook.execute()


if __name__ == "__main__":
    if check_if_sign_date():
        print("It is time to submit your timesheet.")
        send_discord_webhook()
    else:
        print("It isn't time for submitting your timesheet.")
