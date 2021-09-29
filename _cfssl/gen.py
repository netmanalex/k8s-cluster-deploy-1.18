#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement
import subprocess
HOSTS = {
# 将集群内所有的节点写入该字典中，主机名和IP地址要和hosts文件保持一致。
  "k8s-master1": "10.32.34.134",
  "k8s-master2": "10.32.34.135",
  "k8s-master3": "10.32.34.136",
  "k8s-node01": "10.32.34.137",
}
# REQCSR_TPL = """{
#   "key": {
#     "algo": "ecdsa",
#     "size": 384
#   },
#   "names": [
#     {
#       "O": "Bitdeer",
#       "OU": "Cloud 11",
#       "L": "Beijing",
#       "ST": "Beijing",
#       "C": "CN"
#     }
#   ],
#   "CN": "$HOSTNAME$",
#   "hosts": [
#     "127.0.0.1",
#     "localhost",
#     "$IP$",
#     "$HOSTNAME$"
#   ]
# }"""
KUBELET_CSR_TPL = """{
  "key": {
    "algo": "ecdsa",
    "size": 384
  },
  "names": [
    {
      "O": "system:nodes",
      "OU": "Cloud 11",
      "L": "Beijing",
      "ST": "Beijing",
      "C": "CN"
    }
  ],
  "CN": "system:node:$HOSTNAME$"
}"""
# KUBEPROXY_CSR_TPL = """{
#   "key": {
#     "algo": "ecdsa",
#     "size": 384
#   },
#   "names": [
#     {
#       "O": "system:node-proxier",
#       "OU": "Cloud 11",
#       "L": "Beijing",
#       "ST": "Beijing",
#       "C": "CN"
#     }
#   ],
#   "CN": "system:kube-proxy"
# }"""
# MASTERS_CSR_TPL = """{
#   "key": {
#     "algo": "ecdsa",
#     "size": 384
#   },
#   "names": [
#     {
#       "O": "system:masters",
#       "OU": "Cloud 11",
#       "L": "Beijing",
#       "ST": "Beijing",
#       "C": "CN"
#     }
#   ],
#   "CN": "chengcai.bao"
# }"""
# APISERVER_CSR_TPL = """{
#   "key": {
#     "algo": "ecdsa",
#     "size": 384
#   },
#   "names": [
#     {
#       "O": "Bitdeer",
#       "OU": "Cloud 11",
#       "L": "Beijing",
#       "ST": "Beijing",
#       "C": "CN"
#     }
#   ],
#   "CN": "$HOSTNAME$",
#   "hosts": [
#     "127.0.0.1",
#     "localhost",
#     "10.254.0.1",
#     "10.89.17.33",
#     "10.89.17.31",
#     "10.89.17.32",
#     "10.89.17.30"
#   ]
# }"""
# CONTROLLER_MANAGER_CSR_TPL = """{
#   "key": {
#     "algo": "ecdsa",
#     "size": 384
#   },
#   "names": [
#     {
#       "O": "system:kube-controller-manager",
#       "OU": "Cloud 11",
#       "L": "Beijing",
#       "ST": "Beijing",
#       "C": "CN"
#     }
#   ],
#   "CN": "system:kube-controller-manager"
# }"""
# SCHEDULER_CSR_TPL = """{
#   "key": {
#     "algo": "ecdsa",
#     "size": 384
#   },
#   "names": [
#     {
#       "O": "system:kube-scheduler",
#       "OU": "Cloud 11",
#       "L": "Beijing",
#       "ST": "Beijing",
#       "C": "CN"
#     }
#   ],
#   "CN": "system:kube-scheduler"
# }"""
# SERVICE_ACCOUNT_CSR_TPL = """{
#   "key": {
#     "algo": "ecdsa",
#     "size": 384
#   },
#   "names": [
#     {
#       "O": "Bitdeer",
#       "OU": "Cloud 11",
#       "L": "Beijing",
#       "ST": "Beijing",
#       "C": "CN"
#     }
#   ],
#   "CN": "service-accounts"
# }"""
# METRICS_SERVER_CSR_TPL = """{
#   "key": {
#     "algo": "ecdsa",
#     "size": 384
#   },
#   "names": [
#     {
#       "O": "system:metrics-server",
#       "OU": "Cloud 11",
#       "L": "Beijing",
#       "ST": "Beijing",
#       "C": "CN"
#     }
#   ],
#   "CN": "system:metrics-server"
# }"""
if __name__ == '__main__':
    # Node
    for k, v in HOSTS.items():
        with open('req-csr.tmp.json', 'w') as f:
            # f.write(REQCSR_TPL.replace('$HOSTNAME$', k).replace('$IP$', v))
            f.write(KUBELET_CSR_TPL.replace('$HOSTNAME$', k))
            # f.write(APISERVER_CSR_TPL.replace('$HOSTNAME$', k))
            #f.write(METRICS_SERVER_CSR_TPL.replace('$HOSTNAME$', k))
        cfssl_proc = subprocess.Popen([
            'cfssl', 'gencert',
            '-ca', 'ca/ca.pem',
            '-ca-key', 'ca/ca-key.pem',
            '-config', 'cfg/gencert.json',
            'req-csr.tmp.json',
        ], stdout=subprocess.PIPE)
        cfssljson_proc = subprocess.Popen([
            'cfssljson',
            '-bare',
            'certs/{0}'.format(k)
        ], stdin=cfssl_proc.stdout)
        cfssl_proc.stdout.close()
        out, err = cfssljson_proc.communicate()
    # K8S RBAC
    # for k, v in HOSTS.items():
    #     with open('req-csr.tmp.json', 'w') as f:
    #         f.write(KUBELET_CSR_TPL.replace('$HOSTNAME$', k).replace('$IP$', v))
    #     cfssl_proc = subprocess.Popen([
    #         'cfssl', 'gencert',
    #         '-ca', 'ca/ca.pem',
    #         '-ca-key', 'ca/ca-key.pem',
    #         '-config', 'cfg/rbac.json',
    #         'req-csr.tmp.json',
    #     ], stdout=subprocess.PIPE)
    #     cfssljson_proc = subprocess.Popen([
    #         'cfssljson',
    #         '-bare',
    #         'certs/system_node_{0}'.format(k)
    #     ], stdin=cfssl_proc.stdout)
    #     cfssl_proc.stdout.close()
    #     out, err = cfssljson_proc.communicate()