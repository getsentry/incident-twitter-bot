import os
import logging
from requests_oauthlib import OAuth1Session
import requests
import sentry_sdk

from ipaddress import ip_address, ip_network

sentry_sdk.init(
    dsn="https://ec01cb22e492de0be5ee5240cd86d9d9@o1.ingest.us.sentry.io/4508326405931008",
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
    integrations=[
        GcpIntegration(timeout_warning=True),
    ],
)

getsentryhelp_twitter_consumer_key = os.environ.get("getsentryhelp_twitter_consumer_key")
getsentryhelp_twitter_consumer_secret = os.environ.get("getsentryhelp_twitter_consumer_secret")
getsentryhelp_twitter_access_token = os.environ.get("getsentryhelp_twitter_access_token")
getsentryhelp_twitter_access_token_secret = os.environ.get(
    "getsentryhelp_twitter_access_token_secret"
)

# prod status page: https://manage.statuspage.io/pages/t687h3m0nh65/incidents
sentry_atlassian_status_page_id = "t687h3m0nh65"


def validate_request_ip(request):
    # get ip of request
    request_ip_address = ip_address("{}".format(request.access_route[0]))

    # get whitelist of valid ip's from Atlassian
    atlassian_ip_whitelist = requests.get("https://ip-ranges.atlassian.com/").json()[
        "items"
    ]

    # check if ip is a valid one from Atlassian
    for items in atlassian_ip_whitelist:
        if "statuspage" not in items["product"]:
            continue
        if request_ip_address in ip_network(items["cidr"]):
            break
    else:
        error_msg = "IP {} not allowed.".format(request_ip_address)
        raise UserWarning(error_msg)


def validate_incident(request_json):
    if (
        "organization_id" not in request_json["incident"]
        and "monitoring" not in request_json["incident"]
        and "shortlink" not in request_json["incident"]
        and "status_description" not in request_json["page"]
        and "id" not in request_json["page"]
    ):
        logging.error("Incident Validation: incorrect formatted webhook json")
        return False
    else:
        message = "[status] {}: {} {}".format(
            (request_json["incident"]["status"]).capitalize().replace("_"," "),
            request_json["incident"]["incident_updates"][0]["body"],
            request_json["incident"]["shortlink"],
        )
        return message


def validate_component(request_json):
    if (
        "name" not in request_json["component"]
        and "status" not in request_json["component"]
    ):
        logging.error("Component Validation: incorrect formatted webhook json")
        return False
    else:
        message = "[status] {}: {} https://status.sentry.io".format(
            (request_json["component"]["status"]).capitalize().replace("_"," "),
            request_json["component"]["name"],
        )
        return message


def post_to_twitter(payload):
    oauth = OAuth1Session(
        getsentryhelp_twitter_consumer_key,
        client_secret=getsentryhelp_twitter_consumer_secret,
        resource_owner_key=getsentryhelp_twitter_access_token,
        resource_owner_secret=getsentryhelp_twitter_access_token_secret,
    )

    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        logging.exception("Request returned an error: {} {}".format(
                response.status_code, response.text
            ))
    return "Success",200


def main(request):

    # ensure the request is coming from Atlassian
    validate_request_ip(request)
    request_json = request.get_json(silent=True)

    # ensure the webhook is originated from our statuspage
    if "page" not in request_json or "id" not in request_json["page"]:
        raise TypeError("incorrect formatted webhook json")
    elif request_json["page"]["id"] != sentry_atlassian_status_page_id:
        raise UserWarning("not our incident")

    # validate the request and compose the message
    if "incident" in request_json:
        message = validate_incident(request_json)
    elif "component" in request_json:
        message = validate_component(request_json)
        return "Success",200
    else:
        logging.error("no incidnet nor have compnenet")
        return "Success",200

    if message != False:
        return post_to_twitter({"text": message})
    else:
        return "Success",200


if __name__ == "__main__":
    main()
