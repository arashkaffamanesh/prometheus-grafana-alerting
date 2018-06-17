# Prometheus, Grafana amd Alertmanager setup

This repo was cloned from the Github repo of our friends at Giantswarm:

https://github.com/giantswarm/kubernetes-prometheus

With this implementation you can monitor any k8s clusters or external VMs and possibly external endpoints runnig outside of your k8s cluster.

The following adaptions / extentions was needed to provide monitoring and alerting for external VMs (in our case a gateway VM) and use it possibly to monitore other (application) services running on any k8s clusters.

The gateway-grafana-prometheus folder was added to this repo and has her own README.md file and provides 2 palybooks for installing the node-exporter on the Gateway VM along with other helper tools like eat_cpu.py, eat_memory.py and eat_disk.py for testing.

If you're going to play with alerting you need to follow the steps for installing the node-exporter and the helper tools via ansible as described in the [gateway-grafana-prometheus](README file).

In our case we're using an Ubuntu Test VM running on OpenStack to test alerting with Slack, Hipchat or via email.

This implemenation was tested on k8s clusters version 1.10.4 (on minikube, multi-node vagrant cluster and any other k8s clusters).

## Overall architecture

Prometheus, grafana and alertmanager will be installed via the manifests-all.yaml manifest file to the k8s cluster and the prometheus node-exporter will be installed via apt package manager in our case on the Ubuntu Test VM.

The node-exporter exports metrics on the Test VM for black-box monitoring of the Test VM.

On the k8s cluster itself the node-exporter is also deployed via a DaemonSet on each k8s node.

## Adaptions for activating alerting in prometheus configmap.yaml

To activate alerting the following adaption was needed to be done in the configmap.yaml manifest file in the manifests/prometheus folder:

```bash
    # Alertmanager configuration
    alerting:
      alertmanagers:
      - static_configs:
        - targets:
          - alertmanager:9093

    scrape_configs:

      - job_name: 'gateway-node-exporter'
        static_configs:
          - targets: ['10.111.0.4:9100']
```

N.B.: The scrape config with the job name 'gateway-node-exporter' and target 10.111.0.4 (which is the private IP address of the Gateway VM) was added to read the exposed metrics through the node exporter.

## Adaptions for activating alerting through Hipchat

For sending Prometheus alerts to your Slack channel the following adaption is needed to be made in the configmap of the alertmanager:

```bash
- name: 'slack_alert'
      slack_configs:
      - api_url: https://hooks.slack.com/services/xxxxxxxxxx
        channel: '#alerts'
        text: '<!channel>{{ template "slack.devops.text" . }}'
        send_resolved: true
```

N.B.: the api_url can be retrieved through adding a custom integration for "Incoming Webhooks" in Slack app integration. 

## Adaptions for activating alerting through Hipchat

For sending Prometheus alerts to your Hipchat room the following adaption is needed to be made in the configmap of the alertmanager:

```bash
 - name: 'hipchat'
      hipchat_configs:
      - room_id: 1234567
        auth_token: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
        message_format: html
        notify: true
```

N.B.: the room_id and auth_token was retrieved through adding the "PrometheusAlerts" integration to Hipchat. 

## Adaption to alerting rules for CPU usage:

The following adaption was needed to be provided to the cpu-usage.rules under configs/prometheus/rules to be able to receive alerting for high CPU usage:

```bash
name="node-exporter"
```

had to be replaced with (the key 'name' is wrong, it shall be 'job'):

```bash
job="gateway-node-exporter"
```

N.B.: The job name gateway-node-exporter should correspond to the setting in the scrape_configs.

## Ingress configuration

To be able to access the cluster through a public URL, the ingress.yaml definition was added under the manifests/grafana folder.

N.B.: if deploying to other clusters the host value shall be adapted accordingly.

## Deplyoment

By running the build.sh script, the manifests-all.yaml file will be populated with all the neccesary adaptions made above.

```bash
$ ./build.sh
```

After running the build.sh script, the whole deplyoment is as easy as to run:

```bash
kubectl apply -f manifests-all.yaml
```

This will create the namespace `monitoring` and bring up all components in there.

To shut down all components again you can just delete that namespace:
```bash
kubectl delete namespace monitoring
```

## Custom dashboard

After the deployment, please head to:

http://grafana.xxx.kubernauts.io

and import the node-exporter-server-metrics_rev6.json grafana dashboard json file through the grafana dashbaord and choose the data source "prometheus".

N.B.: the node-exporter-server-metrics_rev6.json is provided under the "grafana" folder.

We name te dashboard "Gateway VM Metrics".

Alternatively if you don't have any ingress url defined or you're deploying the whole thing on minkube, you can use "kubectl port-forward" for the grafana-core pod to access the grafana dashbaord through localhost:

```bash
$ k port-forward grafana-core-f796895df-cd89q 3000
```

The username and password for the Grafana dashboard are both "admin".

## Secure the Grafana dashboard through SSL

--> ToDo: use cert-manager

# How to test the various alertings

By running the eat_cpu.py, eat_memory.py and eat_disk.py python scripts as the root user on the Test VM alerting messages will be fired and sent to the "alerts" slack channel or your hipchat chat room, depending on how the tresholds have been defined in the rules files.

# How to access the Prometheus and Alertmanager dashboard

For troubleshooting it might be helpful to access the Prometheus and Alertmanager dashboards.

Use "kubectl port-forward" for the prometheus-core (with the port 9090) and alertmanager pod (with the port 9093) to access the dashboards throuh localhost, e.g.:

Prometheus:
http://localhost:9090

Alertmanager:
http://localhost:9093

# Adapting the thresholds in rules

The thresholds can be adapted in the rules files under:

configs/prometheus/rules

folder.

N.B.: after adapting the rules you shall run "./build.sh" again followed by "k apply -f manifests-all.yaml". It might be a good idea to delete the prometheus-core and alertmanager pods, if the above doesn't work immediately.

## Default Dashboards

If you want to re-import the default dashboards from this setup run this job:
```bash
kubectl apply --filename ./manifests/grafana/grafana-import-dashboards-job.yaml
```

In case the job already exists from an earlier run, delete it before:
```bash
kubectl --namespace monitoring delete job grafana-import-dashboards
```

## More Dashboards

See grafana.net for some example [dashboards](https://grafana.net/dashboards) and [plugins](https://grafana.net/plugins).

- Configure [Prometheus](https://grafana.net/plugins/prometheus) data source for Grafana.<br/>
`Grafana UI / Data Sources / Add data source`
  - `Name`: `prometheus`
  - `Type`: `Prometheus`
  - `Url`: `http://prometheus:9090`
  - `Add`

- Import [Prometheus Stats](https://grafana.net/dashboards/2):<br/>
  `Grafana UI / Dashboards / Import`
  - `Grafana.net Dashboard`: `https://grafana.net/dashboards/2`
  - `Load`
  - `Prometheus`: `prometheus`
  - `Save & Open`

- Import [Kubernetes cluster monitoring](https://grafana.net/dashboards/162):<br/>
  `Grafana UI / Dashboards / Import`
  - `Grafana.net Dashboard`: `https://grafana.net/dashboards/162`
  - `Load`
  - `Prometheus`: `prometheus`
  - `Save & Open`

## Credit

Alertmanager configs and integration in this repository was heavily inspired by the implementation in [kayrus/prometheus-kubernetes](https://github.com/kayrus/prometheus-kubernetes).

## Questions?

Please feel free to ask any questions in our #prometheus slack channel by joining us on Slack:

https://kubernauts-slack-join.herokuapp.com/



