## 生成CA证书
ca.json的内容按需求更改，证书默认10年有效期

证书生成命令如下：
```
# 需要安装cfssl命令
cfssl gencert -initca ca.json|cfssljson -bare ca
```

## 生成服务器证书
修改gen.py脚本
```
例子：
 for k, v in HOSTS.items():
        with open('req-csr.tmp.json', 'w') as f:
            # f.write(REQCSR_TPL.replace('$HOSTNAME$', k).replace('$IP$', v))
            f.write(KUBELET_CSR_TPL.replace('$HOSTNAME$', k))
            ...
修改后，执行以下命令：
python2 gen.py

在certs目录中会找到相应的服务器证书
```