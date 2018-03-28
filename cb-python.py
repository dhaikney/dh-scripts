#!/usr/bin/env python

from couchbase.bucket import Bucket
import cbargs
import time
import couchbase
import sys



def runWorkload(bucket,args):
  document=bytearray(args.size)

  for x in range(0, args.size):
      document[x]=x*27%256;

  for x in range (args.count):
    key = "{0}{1:07d}".format(args.prefix,x)
    success = False
    while not success:
      try:
        result = bucket.set(key, document, format=couchbase.FMT_BYTES)
        print "\radded doc: " + key,
        sys.stdout.flush()
        success = True
      except Exception as e:
        print "Failed to insert "  + key + "with " + str(e)
        time.sleep(1)
  		# result = cb.get(key,replica=True)
  		# print "read: " + key + " from replica"

if __name__ == "__main__":
  args = cbargs.parseArguments()
  bucket = cbargs.connectToBucket(args)
  runWorkload(bucket,args)
