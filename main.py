from valutatrade_hub.cli.interface import CLIInterface
from valutatrade_hub.logging_config import setup_logging


def main():
    # print("Hello world!")

    cli = CLIInterface()
    cli.run()


if __name__ == "__main__":
    main()
