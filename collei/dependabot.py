import itertools
from pathlib import Path

import ruamel.yaml

INTERVALS = [
    "daily",
    "weekly",
    "monthly"
]
MATCHES = {
    "bundler": ["Gemfile"],
    "cargo": ["Cargo.toml"],
    "composer": ["composer.json"],
    "docker": ["Dockerfile"],
    "mix": None,
    "elm": None,
    "gitsubmodule": [".gitmodules"],
    "github-actions": [".github/workflows/*.yml"],
    "gomod": None,
    "gradle": ["build.gradle"],
    "maven": None,
    "npm": ["package.json"],
    "nuget": ["package.config", "*.csproj"],
    "pip": ["requirements.txt", "Pipfile", "pyproject.toml", "setup.py"],
    "pub": None,
    "terraform": None,
    "yarn": None
}
SERVICES = [service for service, glob in MATCHES.items()]


def generate_dependabot_config(interval: str, skip: list[str], force: list[str], verbose: bool):
    path = Path.cwd()

    spec = {}
    updates = []
    spec["version"] = 2
    spec["updates"] = updates

    for ecosystem, globs in MATCHES.items():
        if globs is None:
            if verbose:
                print(f"Ecosystem {ecosystem} is not currently supported by Collei")
            continue

        iterators = [path.glob(glob) for glob in globs]
        objects = list(itertools.chain.from_iterable(iterators))
        valid = any(objects)

        if ecosystem in skip and valid:
            print(f"Skipped valid Ecosystem in use {ecosystem}")
            continue

        if valid or ecosystem in force:
            if ecosystem in force and not valid:
                print(f"Forced generation of configuration for Ecosystem {ecosystem}")

            updates.append({
                "package-ecosystem": ecosystem,
                "directory": "/",
                "schedule": {
                    "interval": interval
                }
            })

            print(f"Added configuration for Ecosystem {ecosystem}")
        else:
            if verbose:
                print(f"Couldn't find any files for Ecosystem {ecosystem}, skipping...")

    yaml = ruamel.yaml.YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.encoding = "utf-8"

    file = path / ".github" / "dependabot.yml"
    file.parent.mkdir(parents=True, exist_ok=True)
    yaml.dump(spec, file)

    print(f"Saved Dependabot configuration to {file}")
