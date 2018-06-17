# Install the node-exporter

To install the node-exporter, please provide the IP for the Gateway VM in hosts.ini and run the playbook

```bash
$ ansible-playbook -i hosts.ini node-exporter-playbook.yml
```

## Check the status on the VM

systemctl status prometheus-node-exporter

[root@gateway-vm system]# netstat -tulpen | grep 9100

tcp6       0      0 :::9100                 :::*                    LISTEN      99         12776890   7158/node_exporter

# Copy the helper tools to the Gateway VM

To copy the helper tools to the Gateway VM, please run the eat-playbook:

```bash
$ ansible-playbook -i hosts.ini eat-playbook.yml
```

