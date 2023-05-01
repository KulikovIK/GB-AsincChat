from src.core import get_app_arguments, Client
import logging
from src.log import config_client_log


_DESCRIPTOR = "client"
LOG = logging.getLogger(_DESCRIPTOR)


def main():
    args = get_app_arguments(_DESCRIPTOR)
    app = Client(host=args.host, port=args.port)
    app.run()


if __name__ == "__main__":
    main()
