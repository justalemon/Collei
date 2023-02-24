import sys
from argparse import ArgumentParser

from .dependabot import INTERVALS, SERVICES, generate_dependabot_config
from .template import use_template


def parse_arguments():
    parser = ArgumentParser(prog="collei",
                            description="Lemon's modding tools")
    subparser = parser.add_subparsers(help="the action to do", dest="action")

    template = subparser.add_parser("template", help="uses a template to create a project or file")
    template.add_argument("name", help="the name of the template to use")

    dependabot = subparser.add_parser("dependabot", help="creates a dependabot configuration file")
    dependabot.add_argument("--interval", help="the interval between updates", choices=INTERVALS,
                            default="weekly")
    dependabot.add_argument("--skip", help="skips specific supported ecosystems", choices=SERVICES,
                            nargs="+")
    dependabot.add_argument("--force", help="forces the generation of specific supported ecosystems", choices=SERVICES,
                            nargs="+")
    dependabot.add_argument("--no-labels", help="doesn't adds the labels", action="store_true")
    dependabot.add_argument("--verbose", help="show extra information", choices=SERVICES,
                            nargs="+")

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.action == "template":
        return use_template(args.name)
    elif args.action == "dependabot":
        return generate_dependabot_config(args.interval, args.skip or [], args.force or [], args.verbose,
                                          args.no_labels)

    return 0


if __name__ == "__main__":
    sys.exit(main())
