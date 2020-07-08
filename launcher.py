import argparse

from mrserver import Server


def main() -> None:

    # Create CLI argument parser.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "port", metavar="port", type=int, help="The port the server should listen to."
    )
    parser.add_argument(
        "max_clients",
        metavar="max_clients",
        type=int,
        help="The number of concurrent connections permissible.",
    )

    # Parse the arguments.
    args = parser.parse_args()

    # Run the server
    server = Server(args.port, args.max_clients)
    server.run()


if __name__ == "__main__":
    main()
