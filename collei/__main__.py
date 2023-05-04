import sys
from argparse import ArgumentParser

from .natives import TYPES, NATIVES, write_natives
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

    natives = subparser.add_parser("natives", help="generator for native enums and stubs")
    natives.add_argument("format", choices=list(NEW_TYPES.keys()),
                         help="the format of the file")
    natives.add_argument("--file",
                         help="the path of the output file or directory")
    natives.add_argument("--lists", choices=list(NATIVES.keys()), nargs="+", default=["gtav"],
                         help="the different lists of natives to add")
    natives.add_argument("--call", action="store_true",
                         help="if the functions should call the natives instead of being stubs")
    natives.add_argument("--comments", action="store_true",
                         help="whether comments with the native documentation should be appended")
    natives.add_argument("--no-extras", action="store_true",
                         help="don't add the extra function declarations for the frameworks")

    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.action == "template":
        return use_template(args.name)
    elif args.action == "dependabot":
        return generate_dependabot_config(args.interval, args.skip or [], args.force or [], args.verbose,
                                          args.no_labels)
    elif args.action == "natives":
        return write_natives(args.file, args.format, args.lists, args.call, args.comments, args.no_extras)

    return 0


if __name__ == "__main__":
    sys.exit(main())
