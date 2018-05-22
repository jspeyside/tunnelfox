import argparse
import logging
import sys

from .manager import TunnelManager


FORMAT = "%(levelname)s[%(filename)s:%(lineno)d] %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
LOG = logging.getLogger(__name__)


def list(args):
    TunnelManager().list()


def create(args):
    tunnel = TunnelManager()
    tunnel.create(args.server, args.port, args.local_port, args.name)


def stop_tunnel(args):
    if not args.num or len(args.num) != 1:
        return
    num = int(args.num[0])
    TunnelManager().stop(num)


def main():
    parser = argparse.ArgumentParser(prog='tunnelfox')

    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='-h additional help')
    ls = subparsers.add_parser('ls', help='list active port forwards')
    ls.set_defaults(func=list)

    new = subparsers.add_parser('new', help='create a new port forward')
    new.add_argument(
        '--port',
        '-p',
        required=True,
        type=int,
        help='The remote port to port forward')
    new.add_argument(
        '--server',
        '-s',
        required=True,
        type=str,
        help='The remote server to port forward')
    new.add_argument(
        '--local-port',
        '-l',
        help=('The local port to forward to the remote end. '
              'Defaults to the same port as the remot port if unspecified.'))
    new.add_argument(
        '--name',
        '-n',
        help='The name to use to connect to the port forward.')
    new.set_defaults(func=create)

    stop = subparsers.add_parser('stop', help='stop')
    stop.add_argument('num', nargs=1)
    stop.set_defaults(func=stop_tunnel)

    opts = parser.parse_args(sys.argv[1:])
    try:
        opts.func(opts)
    except AttributeError:
        parser.print_help()
        exit(0)


if __name__ == '__main__':
    main()
