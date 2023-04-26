import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from git import Repo, InvalidGitRepositoryError
from requests import post, get, delete, patch

CLIENT_ID = "Iv1.ce7db306f0bd3797"
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
BODY_REQUEST = {
    "client_id": CLIENT_ID,
    "scope": "repo"
}
LABELS = [
    {
        "name": "priority: p0 critical",
        "description": "",
        "color": "FF7F00"
    },
    {
        "name": "priority: p1 high",
        "description": "",
        "color": "FF7F00"
    },
    {
        "name": "priority: p2 medium",
        "description": "",
        "color": "FF7F00"
    },
    {
        "name": "priority: p3 low",
        "description": "",
        "color": "FF7F00"
    },
    {
        "name": "priority: p4 not applicable",
        "description": "",
        "color": "FF7F00"
    },
    {
        "name": "status: acknowledged",
        "description": "",
        "color": "0E8A16"
    },
    {
        "name": "status: completed",
        "description": "",
        "color": "0E8A16"
    },
    {
        "name": "status: confirmed",
        "description": "",
        "color": "0E8A16"
    },
    {
        "name": "status: help wanted",
        "description": "",
        "color": "0E8A16",
        "alt": [
            "help wanted"
        ]
    },
    {
        "name": "status: invalid",
        "description": "",
        "color": "0053C0",
        "alt": [
            "invalid"
        ]
    },
    {
        "name": "status: duplicate",
        "description": "",
        "color": "0053C0",
        "alt": [
            "duplicate"
        ]
    },
    {
        "name": "status: needs info",
        "description": "",
        "color": "0053C0"
    },
    {
        "name": "status: needs triage",
        "description": "",
        "color": "0053C0"
    },
    {
        "name": "status: ready to merge",
        "description": "",
        "color": "0E8A16"
    },
    {
        "name": "status: won't fix",
        "description": "",
        "color": "0053C0",
        "alt": [
            "wontfix"
        ]
    },
    {
        "name": "status: 3rd party issue",
        "description": "",
        "color": "0053C0"
    },
    {
        "name": "type: bug",
        "description": "",
        "color": "D4000C",
        "alt": [
            "bug"
        ]
    },
    {
        "name": "type: dependencies",
        "description": "",
        "color": "D31C96"
    },
    {
        "name": "type: documentation",
        "description": "",
        "color": "D31C96",
        "alt": [
            "documentation"
        ]
    },
    {
        "name": "type: feature removal",
        "description": "",
        "color": "D4000C"
    },
    {
        "name": "type: feature request",
        "description": "",
        "color": "D31C96",
        "alt": [
            "enhancement"
        ]
    },
    {
        "name": "type: question",
        "description": "",
        "color": "D31C96",
        "alt": [
            "question"
        ]
    }
]

# https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#device-flow


def get_token():
    """
    Gets the GitHub token of the user.
    """
    started = time.time()

    resp = post("https://github.com/login/device/code", headers=HEADERS, json=BODY_REQUEST)

    if not resp.ok:
        raise ConnectionError("Couldn't request Login Code")

    request = resp.json()
    url = request["verification_uri"]
    user_code = request["user_code"]
    device_code = request["device_code"]
    interval = request["interval"]
    expires = request["expires_in"]

    print(f"Please go to {url} and enter code {user_code} to log in")
    print("The program will continue automatically once you have done so")

    while True:
        if started + expires <= time.time():
            print("Timed out while waiting for the token, please try again", file=sys.stderr)
            return None

        json = {
            "client_id": CLIENT_ID,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code"
        }

        check = post("https://github.com/login/oauth/access_token", headers=HEADERS, json=json)
        json = check.json()

        if "error" not in json:
            return json["access_token"], json["refresh_token"], json["refresh_token_expires_in"]

        time.sleep(interval)


def update_tags():
    try:
        path = Path.cwd()
        repo = Repo(path)
        origin = repo.remote("origin")
    except InvalidGitRepositoryError:
        print(f"Couldn't find Git repo at {path}", file=sys.stderr)
        return 1
    except ValueError:
        print("Couldn't a remote called origin", file=sys.stderr)
        return 2

    parsed = urlparse(origin.url.replace(".git", ""))

    if parsed.netloc != "github.com":
        print(f"The origin remote does not appears to be on GitHub (got {parsed.netloc})", file=sys.stderr)
        return 3

    stem = parsed.path.lstrip("/").split("/")
    repo_owner = stem[0]
    repo_name = stem[1]

    tokens = get_token()

    if tokens is None:
        return 4

    access, refresh, expiration = tokens

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {access}",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    labels_resp = get(f"https://api.github.com/repos/{repo_owner}/{repo_name}/labels", headers=headers)

    if not labels_resp.ok:
        print(f"Repo does not appears to exist", file=sys.stderr)
        return 5

    existing_labels = {x["name"]: x for x in labels_resp.json()}

    for label in LABELS:
        name = label["name"]
        color = label["color"]
        alternatives = label.get("alt", [])
        description = label["description"]

        matched = [x for x in alternatives if x in existing_labels]

        if matched:
            if len(matched) > 1:
                print(f"Warning: Label {name} was found with more than 1 match, will only keep first one")

                for unused in matched[1:]:
                    label_delete = delete(f"https://api.github.com/repos/{repo_owner}/{repo_name}/labels/{unused}",
                                          headers=headers)

                    print(f"Deleted label {unused} with code {label_delete.status_code}")

            primary = matched[0]

            update = {
                "new_name": name,
                "color": color,
                "description": description
            }

            label_update = patch(f"https://api.github.com/repos/{repo_owner}/{repo_name}/labels/{primary}",
                                 headers=headers, json=update)
            print(f"Updated label {name} with code {label_update.status_code}")
        else:
            add = {
                "name": name,
                "color": color,
                "description": description
            }

            label_create = post(f"https://api.github.com/repos/{repo_owner}/{repo_name}/labels",
                                 headers=headers, json=add)
            print(f"Create label {name} with code {label_create.status_code}")

    print("Done! Synchronized all labels!")
    return 0
