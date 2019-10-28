#!/usr/bin/python
import netifaces
import netaddr
import argparse
from time import sleep
#from arprequest import ArpRequest
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--interface', dest='interface', help='Top-level interface to use', default='enp0s3')
parser.add_argument('-d', '--duration', dest='duration', help='Total duration to run (seconds)', default=3600, type=int)
parser.add_argument('-c', '--clients', dest='clients', help='Number of clients to spawn', default=10, type=int)
parser.add_argument('-n', '--dry-run', dest='dry_run', action='store_true', default=False)
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False)
args = parser.parse_args()

top_ip = netifaces.ifaddresses(args.interface)[netifaces.AF_INET][0]['addr']
top_mask = netifaces.ifaddresses(args.interface)[netifaces.AF_INET][0]['netmask']
top_netblock = str(netaddr.IPNetwork('%s/%s' % (top_ip, top_mask)).prefixlen)

thirdoctet_increment = 0
fourthoctet_base = 5
fourthoctet_increment = 0

for sub_ip in range(args.clients):

    thirdoctet = int(top_ip.split('.')[2])
    fourthoctet = sub_ip + fourthoctet_base + fourthoctet_increment
    new_ip = '.'.join(top_ip.split('.')[0:2]) + '.' + str(thirdoctet + thirdoctet_increment) + '.' + str(fourthoctet)

#    retry_increment = 1
#    ar = ArpRequest(new_ip, args.interface)
#    while ar.request():
#        new_ip = '.'.join(top_ip.split('.')[0:2]) + '.' + str(thirdoctet + thirdoctet_increment) + '.' + str(sub_ip + fourthoctet_increment + retry_increment)
#        retry_increment = retry_increment + 1
#        ar = ArpRequest(new_ip, args.interface)

    if new_ip.split('.')[3] == '255':
        thirdoctet_increment = thirdoctet_increment + 1
        fourthoctet_increment = fourthoctet_increment - 255

    if args.verbose:
        print('creating interface %s on %s' % (new_ip, args.interface))
        print('running "./gen.py -s %s"' % (new_ip))

    if not args.dry_run:
        subprocess.call(['/sbin/ip', 'addr', 'add', '%s/%s' % (new_ip, top_netblock), 'dev', args.interface])

        p = subprocess.Popen(['./gen.py', '-s', new_ip])