#!/bin/bash
export ETCDCTL_API=3
etcdctld="etcdctl --endpoints=10.32.34.134:2379,10.32.34.135:2379,10.32.34.136:2379 --cacert=./_cfssl/ca/ca.pem --cert=./_cfssl/certs/k8s-master1.pem  --key=./_cfssl/certs/k8s-master1-key.pem"
$etcdctld endpoint status
$etcdctld endpoint health --