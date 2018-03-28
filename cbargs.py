#!/usr/bin/env python

from couchbase.bucket import Bucket
import time
import random
import couchbase
import sys
import argparse



def connectToBucket(args):
  conn_string = "couchbase://" + args.node + '/' + args.bucket
  if args.user != "":
    # conn_string += "?username={0}&select_bucket=true".format(args.user)
    conn_string += "?username={0}&select_bucket=true&tracing={1}".format(args.user,args.compression)

  print "connecting to ", conn_string
  return Bucket(conn_string, timeout=args.timeout,password=args.password)

def parseArguments():
  parser = argparse.ArgumentParser(description='Throw some docs in a bucket using the couchbase python client')
  parser.add_argument('--node', '-n', default="localhost", help='Cluster Node to connect to')
  parser.add_argument('--bucket', '-b', default="charlie", help='Bucket to connect to')
  parser.add_argument('--password', '-p',default="password", help='User password')
  parser.add_argument('--user', '-u',default="Administrator", help='Username')
  parser.add_argument('--prefix', '-k',default="CBPY_", help='Key Prefix')
  parser.add_argument('--size', '-s', default=256, type=int, help='Document size in bytes')
  parser.add_argument('--timeout', '-t', default=2, type=int, help='Operation Timeout')
  parser.add_argument('--count', '-c', default=1000, type=int, help='Number of documents to insert')
  parser.add_argument('--compression', '-z', default="off", help='Compression behaviour (on | off)')
  return parser.parse_args()


if __name__ == "__main__":
  print "I'm just the args parser"
