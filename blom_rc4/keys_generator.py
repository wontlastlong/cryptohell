#from sage.all import *
import config_generator as config
import argparse
import os
import numpy as np
from Crypto.Util.number import getPrime, getRandomRange, isPrime, long_to_bytes
import struct
import base64

#print config.CONFIG


parser = argparse.ArgumentParser(description='Generate keys for Blom\'s scheme.')
parser.add_argument('outdir', help='directory for resulting keys')
parser.add_argument('-n', '--network_size', type=int, default=config.CONFIG['network_size'],
    nargs='?', help='amount of nodes to generate keys for')
parser.add_argument('-s', '--strength', type=int, default=config.CONFIG['strength'],
    nargs='?', help='secure parameter, i.e. amount of keys needed to compromise system')
parser.add_argument('-k', '--key_size', type=int, default=config.CONFIG['key_size'],
    nargs='?', choices=range(40, 2048), metavar='[40-2048]', help='shared key size')

args = parser.parse_args()

# TODO: dir exists or no, and stuff

N = args.network_size
lambd = args.strength
q = getPrime(args.key_size)
# N = 5
# lambd = 3
# q = getPrime(8)

# generate s such that s^1, s^2, ..., s^N are all different
# this ensures that any (lambda + 1) columns in Vandermonde are linearly independent
while True:
    s = getRandomRange(2, q - 1)
    powers = {pow(s, i + 1, q) : i for i in range(N)}

    if len(powers) == N:
        break

powers = np.array(powers.keys())
#powers = np.array([2, 3, 5])

vander = [[pow(x, i, q) for x in powers] for i in range(lambd + 1)]
G = np.array(vander, dtype=object)

d = [[getRandomRange(0, q) for j in range(i)] + [0]*(lambd + 1 - i) for i in range(lambd + 1)]
D = np.array(d)
D = D + D.T

for i in range(lambd + 1):
    D[i, i] = getRandomRange(0, q)

A = np.dot(D, G).T % q

assert np.array_equal(np.dot(A, G) % q, np.dot(A, G).T % q)

pub_a = G[:,0]
prv_a = A[0]

pub_b = G[:,2]
prv_b = A[2]

assert np.array_equal(np.dot(prv_a, pub_b) % q, np.dot(prv_b, pub_a) % q)


def write_node_keys(i_node, verbose=False):
    if verbose:
        print 'Writing {} node data...'.format(i_node)

    pub_data = b''
    pub_data += struct.pack('<H', args.key_size)

    t = long_to_bytes(q)
    pub_data += struct.pack('<H', len(t))
    pub_data += t

    pub_data += struct.pack('<H', lambd + 1)

    prv_data = pub_data
    for i in range(lambd + 1):
        t = long_to_bytes(G[i, i_node])
        pub_data += struct.pack('<H', len(t))
        pub_data += t

        t = long_to_bytes(A[i_node, i])
        prv_data += struct.pack('<H', len(t))
        prv_data += t

    pub_file = open(args.outdir + '/node_{}.pub'.format(i_node), 'wb')
    pub_file.write(base64.b64encode(pub_data))
    pub_file.close()

    prv_file = open(args.outdir + '/node_{}.prv'.format(i_node), 'wb')
    prv_file.write(base64.b64encode(prv_data))
    prv_file.close()

for i in range(N):
    write_node_keys(i)


