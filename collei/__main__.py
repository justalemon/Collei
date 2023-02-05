from argparse import ArgumentParser


def parse_arguments():
    parser = ArgumentParser(prog="collei",
                            description="Lemon's modding tools")
    subparser = parser.add_subparsers(help="the action to do")

    return parser.parse_args()


def main():
    args = parse_arguments()


if __name__ == "__main__":
    main()
