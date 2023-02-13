import sys
from argparse import ArgumentParser

from .template import use_template


def parse_arguments():
    parser = ArgumentParser(prog="collei",
                            description="Lemon's modding tools")
    subparser = parser.add_subparsers(help="the action to do", dest="action")

    template = subparser.add_parser("template", help="uses a template to create a project or file")
    template.add_argument("name", help="the name of the template to use")

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.action == "template":
        return use_template(args.name)

    return 0


if __name__ == "__main__":
    sys.exit(main())
