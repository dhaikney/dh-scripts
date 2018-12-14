#!/usr/bin/env python

from txcouchbase.bucket import Bucket
from twisted.internet import reactor,task
from text_histogram import histogram
import cbargs
import time
from couchbase import FMT_BYTES
import sys

NUM_CLIENTS=16
BATCH_SIZE=10
RATE_LIMIT=5000
NUM_ITERATIONS=1

clients=[]
timings = []
args = {}
finished_runners = 0

def exit_handler():
  print "HISTOGRAM"
  histogram(timings)
  reactor.stop()


def connectToBucket(args):
  conn_string = "couchbase://" + args.node + '/' + args.bucket
  if args.user != "":
    # conn_string += "?username={0}&select_bucket=true".format(args.user)
    conn_string += "?username={0}&select_bucket=true&compression={1}".format(args.user,args.compression)

  print "connecting to ", conn_string
  return Bucket(conn_string, timeout=args.timeout,password=args.password)

class Runner(object):
  def __init__(self, index):
    self.cb = clients[index]
    self.index = index
    self.iteration = 0
    self.batch_count = 0
    self.num_keys    = (args.count / NUM_CLIENTS)
    self.num_batches = self.num_keys / BATCH_SIZE
    self.start_key   = self.num_keys * index
    self.end_key     = self.start_key + self.num_keys
    self.value = b'V' * args.size
    self.emitter = task.LoopingCall(self.emit_batch)
    self.emitter.start(float(NUM_CLIENTS * BATCH_SIZE) / RATE_LIMIT)


  def generate_batch(self,batch_num):
    kv = {}
    start = self.start_key + (batch_num * BATCH_SIZE)
    print "{} {}".format(start, start + BATCH_SIZE)
    for x in range(start, (start + BATCH_SIZE)):
      key = "{}{}_{}".format(args.prefix,str(self.index),str(x))
      kv[key] = self.value
    return kv

  def emit_batch(self):
    if self.batch_count >= (self.num_batches * NUM_ITERATIONS):
      print "Stopping Runner {}".format(self.index)
      self.emitter.stop()
      global finished_runners
      finished_runners += 1
      if finished_runners == NUM_CLIENTS:
        exit_handler()
      return

    batch_num = self.batch_count % self.num_batches

    kv = self.generate_batch(batch_num)
    start_time = time.time() * 1000
    rv = self.cb.upsertMulti(kv, format=FMT_BYTES,replicate_to=1)
    # rv = self.cb.upsert("hello", {"doc":"hello"})
    rv.addCallback(self.result_handler, batch_num,start_time)
    rv.addErrback(self.error_handler, batch_num)
    self.batch_count += 1

  def result_handler(self,res,batch_num,start_time):
    end_time = time.time() * 1000
    duration = end_time - start_time
    timings.append(duration)

  def error_handler(self,err,batch_num):
    print "ERROR on batch {}:{}".format(self.index,batch_num)
    for key, result in err.value.all_results.items():
        print key,result.rc


if __name__ == "__main__":
  args = cbargs.parseArguments()
  for x in range (NUM_CLIENTS):
    client = connectToBucket(args)
    clients.append(client)
    r = Runner(x)
reactor.suggestThreadPoolSize(30)
reactor.run()
print "Bye"