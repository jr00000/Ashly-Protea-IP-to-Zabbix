#!/usr/bin/env python3

import sys
import os
import argparse
from ashly import AshlyAPI
from ashly import int2hex
import ashly
import socket
import json
from setproctitle import setproctitle


dspcommands = {'OPT_MUTE_OUTPUT':{'command':'020200', 'type':3},
'OPT_MUTE_INPUT':{'command':'020201', 'type':3},
'OPT_METER_OUTPUT':{'command':'410200', 'type':3},
'OPT_METER_TEMP':{'command':'420200', 'type':3},
'OPT_METER_CURRENT':{'command':'430200', 'type':3},
'OPT_CHANNEL_PROTECT':{'command':'460200', 'type':3}}


def process_cli(argv):
    parser = argparse.ArgumentParser(description='Gep data about Ashly device channel')
    parser.add_argument('host', nargs=1, help='host name or ip address of Ashly device')
    parser.add_argument('channel', nargs=1, type=int, help='Ashly DSP channel number (starting from 0)')
    parser.add_argument('-p','--port', default=ashly.def_ashly_port, required=False, dest='port',
        type=int, help='UDP port on Ashly device')
    parser.add_argument('-t','--timeout', default=ashly.def_ashly_timeout, required=False, dest='timeout',
        type=int, help='Data waiting timeout in ms')
    parser.add_argument('-r','--retry', default=ashly.def_ashly_retry, required=False, dest='retry',
        type=int, help='Number of retries')
    return parser.parse_args(argv)


def main(argv = sys.argv[1:]):
    try:
        exitcode = 0
        result = ''
        scriptname = os.path.splitext(os.path.basename(__file__))[0]
        setproctitle(scriptname)
        args = process_cli(argv)
        ipaddress = socket.gethostbyname(args.host[0])
        channel = int2hex(args.channel[0])
        for icommand, vcommand in dspcommands.items():
            vcommand['command'] = vcommand['command'] + channel
        ashly = AshlyAPI(timeout=args.timeout, retry=args.retry)
        ashly.socket_open()
        macaddress = ashly.getmac(ipaddress, args.port)
        if macaddress:
            channel_info = ashly.run_commands(ipaddress, args.port, dspcommands, macaddress)
            ashly.socket_close()
            result = json.dumps(channel_info)
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

