#!/usr/bin/env python

import lxml.etree as ET
from argparse import ArgumentParser
from ncclient import manager
from ncclient.operations import RPCError
import time

def notify_cb(notif):
    data = ET.fromstring(notif.xml)
    print(ET.tostring(data, pretty_print=True))

def err_cb(e):
    print(e)

if __name__ == '__main__':

    parser = ArgumentParser(description='Usage:')

    # script arguments
    parser.add_argument('-a', '--host', type=str, required=True,
                        help="Device IP address or Hostname")
    parser.add_argument('-u', '--username', type=str, required=True,
                        help="Device Username (netconf agent username)")
    parser.add_argument('-p', '--password', type=str, required=True,
                        help="Device Password (netconf agent password)")
    parser.add_argument('--port', type=int, default=830,
                        help="Netconf agent port")
    parser.add_argument('--period', type=int, default=1000,
                        help="Time period to poll in 100ths of seconds")
    args = parser.parse_args()

    # connect to netconf agent
    with manager.connect(host=args.host,
                         port=args.port,
                         username=args.username,
                         password=args.password,
                         timeout=90,
                         hostkey_verify=False,
                         device_params={'name': 'default'}) as m:

        # execute netconf operation
        # subscribe to all interface input errors.
        try:
            response = m.establish_subscription(notify_cb, err_cb, '/if:interfaces-state/interface/statistics/in-errors', args.period).xml
            data = ET.fromstring(response)
        except RPCError as e:
            data = e._raw

        # print result of subscription request
        print(ET.tostring(data, pretty_print=True))

        # wait for published notifications
        while True:
            time.sleep(int(args.period / 100))
