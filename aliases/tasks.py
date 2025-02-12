import datetime

import requests
from celery import shared_task
from django.conf import settings


@shared_task
def sync_alias_to_mailgun(alias_id):
    from aliases.models import Alias

    alias = Alias.objects.get(id=alias_id)
    recipients = ",".join([r.email_address for r in alias.recipients.all()])

    url = "https://api.mailgun.net/v3/routes"
    auth = ("api", settings.MAILGUN_API_KEY)
    headers = {"Content-Type": "multipart/form-data"}
    data = {
        "priority": 0,
        "description": f"apps managed DO NOT EDIT - {alias.alias}@{alias.domain}",
        "expression": f'match_recipient("{alias.alias}@{alias.domain}")',
        "action": [f'forward("{recipients}")', "stop()"],
    }

    if alias.mailgun_id:
        url += f"/{alias.mailgun_id}"
        data["id"] = alias.mailgun_id
        print("PUT", url, data, headers, auth)
        response = requests.put(url, params=data, headers=headers, auth=auth)
        response.raise_for_status()
        data = response.json()
        alias.mailgun_id = data["id"]
    else:
        print("POST", url, data, headers, auth)
        response = requests.post(url, params=data, headers=headers, auth=auth)
        response.raise_for_status()
        data = response.json()
        alias.mailgun_id = data["route"]["id"]

    alias.mailgun_updated_at = datetime.datetime.now(datetime.UTC)

    alias.save()
