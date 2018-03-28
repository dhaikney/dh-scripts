#!/bin/bash

# DH 5-Apr-2017
# Automatically setup a cluster_run spock cluster

if [ "$#" != 1 ]
then
    echo "Usage $0: #nodes"
    exit
fi

NUM_NODES=$1

FIRST_NODE=127.0.0.1:9000
BUCKET_NAME=charlie
BUCKET_TYPE=couchbase #ephemeral #couchbase  # memcached
# BUCKET_TYPE=ephemeral

BUCKET_REPLICA=1
QUOTA=512
USER=Administrator
PASS=password


cd ~/dev/cb-server/install/bin
./couchbase-cli cluster-init -c $FIRST_NODE --cluster-username=$USER --cluster-password=$PASS \
 --cluster-port=9000 --cluster-ramsize=${QUOTA} --cluster-name="DH Dev Cluster" --services data



if [ "$NUM_NODES" -gt 1 ]
then
 # 2 nodes, last port is 9001 
 let LAST_PORT="9000 + ${NUM_NODES} - 1"
 for port in `seq 9001 $LAST_PORT`
  do
    echo Adding $port to the cluster
    couchbase-cli server-add -c $FIRST_NODE \
    				--user=${USER} \
    				--password=${PASS} \
           --server-add=127.0.0.1:${port} \
           --server-add-username=${USER} \
           --server-add-password=${PASS}

  done
fi
#
# A rebalance is necessary to ensure all nodes added above are fully introduced to the
# cluster. This is best performed before adding buckets
#
couchbase-cli rebalance -c ${FIRST_NODE} --user=${USER} --password=${PASS}


#
# Create a couchbase-type bucket using the credentials supplied above
#
echo "Creating Bucket"
couchbase-cli bucket-create -c ${FIRST_NODE} \
				--user=${USER} \
				--password=${PASS} \
                --bucket=${BUCKET_NAME} \
                --bucket-ramsize=${QUOTA} \
                --bucket-replica=${BUCKET_REPLICA} \
                --bucket-type=${BUCKET_TYPE}


echo Adding User ${BUCKET_NAME}:${PASS}
./couchbase-cli user-manage -c 127.0.0.1:9000  -u Administrator -p ${PASS} \
 --set --rbac-username ${BUCKET_NAME} --rbac-password ${PASS} --roles bucket_full_access[${BUCKET_NAME}] --auth-domain local
echo "Cluster available at http://${FIRST_NODE}"
