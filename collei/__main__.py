import json
import sys
import uuid
from argparse import ArgumentParser
from os import environ
from pathlib import Path
from urllib.parse import urlparse

import requests
from git import Repo, InvalidGitRepositoryError
from jinja2 import Environment, FileSystemLoader

PARAMETER_TYPES = {
    "int": int,
    "str": str,
    "bool": bool
}


def get_git_params():
    try:
        path = Path.cwd()
        repo = Repo(path)
    except InvalidGitRepositoryError:
        return {}

    parameters = {}

    for remote in repo.remotes:
        url = remote.url.replace(".git", "")
        parsed = urlparse(url)

        if parsed.hostname == "github.com":
            split = parsed.path.split("/")[1:]
            parameters["github"] = {
                "user": split[0],
                "repo": split[1]
            }

    return parameters


def get_latest_nuget_package_version(name: str):
    resp = requests.get(f"https://api.nuget.org/v3-flatcontainer/{name}/index.json")

    if resp.ok:
        data = resp.json()
        versions = data["versions"]
        return versions[-1]
    else:
        print(f"Couldn't fetch latest version of {name}: Code {resp.status_code}", file=sys.stderr)
        return None


def parse_arguments():
    parser = ArgumentParser(prog="collei",
                            description="Lemon's modding tools")
    subparser = parser.add_subparsers(help="the action to do", dest="action")

    template = subparser.add_parser("template", help="uses a template to create a project or file")
    template.add_argument("name")

    return parser.parse_args()


def format_default(default, param_type: str):
    if default is None:
        return ""
    elif param_type == "bool":
        return "y" if default else "n"
    else:
        return str(default)


def use_template(name: str):
    template = Path(__file__).parent / "templates" / name

    if not template.is_dir():
        print("Template does not exists", file=sys.stderr)
        return 5

    metadata = template / "template.json"

    if not metadata.is_file():
        print("Template metadata is not present", file=sys.stderr)
        return 6

    content = metadata.read_text(encoding="utf-8")

    try:
        parameters = json.loads(content)
    except json.JSONDecodeError:
        print("Template metadata is invalid", file=sys.stderr)
        return 7

    if any(x for x in parameters if x["type"] not in PARAMETER_TYPES):
        print("Invalid parameter type", file=sys.stderr)
        return 8

    parsed_parameters = {}
    params = {
        "nuget": {
            "latest": get_latest_nuget_package_version
        },
        "uuid": {
            "random": lambda: str(uuid.uuid4())
        },
        **get_git_params()
    }

    for parameter in parameters:
        identifier = parameter["id"]
        title = parameter["title"]
        type_name = parameter["type"]
        env_name = f"COLLEI_TEMPLATE_{name.upper()}_{identifier.upper()}"
        default = environ.get(env_name, None) or parameter["default"]

        if isinstance(default, str) and default.startswith("TEMPLATE:"):
            dict_path = default.replace("TEMPLATE:", "").split(".")

            current = params

            try:
                for section in dict_path:
                    current = current[section]
            except KeyError:
                pass
            else:
                if not isinstance(current, dict):
                    default = current
        elif isinstance(default, str) and default.startswith("NUGET:"):
            package_name = default.replace("NUGET:", "")
            version = get_latest_nuget_package_version(package_name)

            if not version:
                return 9

            default = version

        answer = None
        formatted_default = format_default(default, type_name)
        prompt = f"{title} ({formatted_default}) [{type_name}]: "

        while not answer:
            answer = input(prompt)

            if answer and type_name == "bool":
                lower = answer.lower()

                if lower == "y" or lower == "yes":
                    answer = True
                    break
                elif lower == "n" or lower == "no":
                    answer = False
                    break
                elif lower != "":
                    answer = None
                    continue

            if not answer and default is not None:
                answer = default
                break

        class_type = PARAMETER_TYPES[type_name]
        parsed = class_type(answer)

        if parsed:
            parsed_parameters[identifier] = parsed

    params["input"] = parsed_parameters

    cwd = Path.cwd()
    loader = FileSystemLoader(searchpath=template, encoding="utf-8")
    env = Environment(loader=loader)
    for template_name in env.list_templates(filter_func=lambda x: x.lower() != "template.json"):
        template = env.get_template(template_name)
        render = template.render(params)

        name = env.from_string(template_name).render(params)

        path = cwd / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render, encoding="utf-8")

    return 0


def main():
    args = parse_arguments()

    if args.action == "template":
        return use_template(args.name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
