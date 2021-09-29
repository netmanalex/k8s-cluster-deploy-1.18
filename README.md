## VERSION
- ansible: v2.9.10
- docker: v19.03.5
- kubeadm: v1.18.8
- kubectl: v1.18.8
- kubelet: v1.18.8
- flannel: v0.13
- etcd: 3.4.3
- nginx-ingress-controller: 0.30.0

---
## 脚本介绍
### 关于kubernetes-1.18.8
脚本中的二进制程序“kubeadm”已经重编译，更改了证书有效时间为10年。

### Playbook 介绍
```
# K8S集群初始化操作，所有节点都要执行。
01-cluster-init.yaml  
# k8s集群ETCD服务部署，默认装在master节点上。
02-master-etcd-deploy.yaml  
# k8s集群master部署，在inventory/group_vars/cluster文件内容标注master节点。
03-master-cluster-deploy.yaml  
# k8s集群node节点部署，由inventory/hosts文件中标注。默认除master节点外的全部主机都会部署。注意，已经安装过得node节点请注释。
04-node-join.yaml 
# k8s集群ingress-nginx部署，在inventory/group_vars/cluster文件内容标注ingress节点。
05-master-ingress-nginx.yaml  
```
---
## 安装前准备
### 一，校对配置文件及host信息
- ./inventory/hosts
```
[cluster]
10.32.34.134     hostname={{kube_master1_name}}
10.32.34.135     hostname={{kube_master2_name}}
10.32.34.136     hostname={{kube_master3_name}}
10.32.34.137     hostname=k8s-node01
```

> **注意master节点的hostname命名，在./inventory/group_vars/cluster中配置。node节点的hostname可以随意配置。**

- ./inventory/group_vars/cluster
```
...
# 负载均衡或者slb地址
kube_master_vip: 10.32.34.138
# master节点信息
kube_master1_name: k8s-master1
kube_master1_addr: 10.32.34.134
kube_master2_name: k8s-master2
kube_master2_addr: 10.32.34.135
kube_master3_name: k8s-master3
kube_master3_addr: 10.32.34.136

# 注意格式，必须是hosts文件ip列表中的hostname字段
ingress_nginx_server: ['k8s-node01']
...
```

> **请确认好master1-3的IP地址和hostname。保证IP地址和hosts文件内相同。否则部署会失败。**
> **kube_master_vip变量留空则不使用负载均衡服务。**

- ._cfssl/gen.py
```
...
HOSTS = {
# 将集群内所有的节点写入该字典中，主机名和IP地址要和hosts文件保持一致。
  "k8s-master1": "10.32.34.134",
  "k8s-master2": "10.32.34.135",
  "k8s-master3": "10.32.34.136",
  "k8s-node01": "10.32.34.137",
}
...
```
> **将集群内所有的节点写入该字典中，主机名和IP地址要和hosts文件保持一致。**
---
### 二，生成CA证书和kubelet证书

#### 生成CA证书
1. ca.json的内容按需求更改，证书默认10年有效期。

2. 证书生成命令如下：
```
# 需要安装cfssl命令
]# cd _cfssl/ca/
]# cfssl gencert -initca ca.json|cfssljson -bare ca
```

#### 生成各个节点的kubelet证书
> **kubelet 证书，无论是master还是node都要用到这个证书。**

修改gen.py脚本，注意脚本中的host 地址列表，也需要修改。
```
]# cd _cfssl

HOSTS = {
# 将集群内所有的节点写入该字典中，主机名和IP地址要和hosts文件保持一致。
  "k8s-master1": "10.32.34.134",
  "k8s-master2": "10.32.34.135",
  "k8s-master3": "10.32.34.136",
  "k8s-node01": "10.32.34.137",
}
...
...
 for k, v in HOSTS.items():
        with open('req-csr.tmp.json', 'w') as f:
            # 生成kubelet的证书
            f.write(KUBELET_CSR_TPL.replace('$HOSTNAME$', k))
            ...
```
#修改后，执行以下命令：
]# cd _cfssl
]# mkdir certs 
]# python2 gen.py

> **可在certs目录中会找到相应的服务器证书**

---
## 部署kubernetes集群

### 1. 初始化操作

```
# 可master，node节点全局使用
ansible-playbook -i inventory/hosts -e "group=cluster" playbook/01-cluster-init.yaml  --key-file "/root/.ssh/sgp_id_rsa"
```

### 2. 部署etcd集群

```
# master节点
ansible-playbook -i inventory/hosts -e "group=cluster" playbook/02-master-etcd-deploy.yaml  --key-file "/root/.ssh/sgp_id_rsa"
```

### 3. 部署master节点

```
# master节点
 ansible-playbook -i inventory/hosts -e "group=cluster" playbook/03-master-cluster-deploy.yaml  --key-file "/root/.ssh/sgp_id_rsa"
```
### 4. 部署node节点

```
# node节点
ansible-playbook -i inventory/hosts -e "group=cluster" playbook/04-node-join.yaml  --key-file "/root/.ssh/sgp_id_rsa"
```

### 5. 部署ingress-nginx 
> **按需执行**
```
# ingress-nginx
ansible-playbook -i inventory/hosts -e "group=cluster" playbook/05-master-ingress-nginx.yaml  --key-file "/root/.ssh/sgp_id_rsa"
```
