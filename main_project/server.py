from src.core import get_app_arguments, Server
import logging
from src.log import config_server_log


_DESCRIPTOR = "server"
LOG = logging.getLogger(_DESCRIPTOR)

def main():
    args = get_app_arguments(_DESCRIPTOR)
    app = Server(host=args.host, port=args.port)
    app.run()


if __name__ == "__main__":
    main()
