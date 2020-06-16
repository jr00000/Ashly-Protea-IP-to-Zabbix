#!/usr/bin/env python3

import sys
import os
import argparse
from ashly import AshlyAPI
import ashly
import socket
from setproctitle import setproctitle


ashly_discovery_command = '420200'


def process_cli(argv):
    parser = argparse.ArgumentParser(description='Discover channels on Ashly device')
    parser.add_argument('host', nargs=1, help='host name or ip address of Ashly device')
    parser.add_argument('-p','--port', default=ashly.def_ashly_port, required=False, dest='port',
                        type=int, help='UDP port on Ashly device')
    parser.add_argument('-t','--timeout', default=ashly.def_ashly_timeout, required=False, dest='timeout',
                        type=int, help='Data waiting timeout in ms')
    parser.add_argument('-r','--retry', default=ashly.def_ashly_retry, required=False, dest='retry',
                        type=int, help='Number of retries')
    return parser.parse_args(argv)


def format_zabbix_discovert(channels):
    result = '{\n\t"data":[\n'
    if channels:
        for channel in channels:
            result = result + '\t{\n\t\t"{#CHANNELINDEX}":' + str(channel) + '\n\t},\n'
        result = result[:-2] + '\n'
    result = result+'\t]\n}\n'
    return result


def main(argv = sys.argv[1:]):
    try:
        exitcode = 0
        result = ''
        scriptname = os.path.splitext(os.path.basename(__file__))[0]
        setproctitle(scriptname)
        args = process_cli(argv)
        ipaddress = socket.gethostbyname(args.host[0])
        ashly = AshlyAPI(timeout=args.timeout, retry=args.retry)
        ashly.socket_open()
        macaddress = ashly.getmac(ipaddress, args.port)
        if macaddress:
            channels = ashly.run_command_for_all_channels(ipaddress, args.port,
                ashly_discovery_command, macaddress)
            ashly.socket_close()
            result = format_zabbix_discovert(channels)
        else:
            ashly.socket_close()
            exitcode = 2
    except:
        exitcode = 1
        result=''
    finally:
        print(result)
        return exitcode

if __name__ == "__main__":
    sys.exit(main())

