# OpenShift Alertmanager Webhook Receiver

This repository contains `webhook.py`, a simple webhook receiver designed to validate alerts sent by OpenShift's Alertmanager. The webhook processes incoming alerts and provides a structured way to inspect and verify their delivery.


## Prerequisites

Before setting up the webhook receiver, ensure you have the following:

- A server running **Linux** (Ubuntu, CentOS, or any other modern distribution)
- **Python 3.x** installed
- Required Python packages: `flask` and `requests`
- Firewall rules allowing inbound traffic on the webhook port
- A DNS entry pointing to the webhook receiver's public or internal IP
- OpenShift cluster with Alertmanager configured to send alerts


## Installation

1. **Install Required Packages**

   ```sh
   sudo apt update && sudo apt install python3 python3-pip -y
   pip3 install flask requests
   ```

2. **Run the Webhook Receiver**

   ```sh
   python3 webhook.py
   ```

   By default, it runs on `http://0.0.0.0:9099`. You can change the port in the script if needed.


## Firewall Configuration

Ensure the webhook port (e.g., 9099) is accessible by configuring the firewall:

```sh
sudo ufw allow 9099/tcp
```

For **firewalld** (RHEL/CentOS-based systems):

```sh
sudo firewall-cmd --add-port=9099/tcp --permanent
sudo firewall-cmd --reload
```


## DNS Setup

Ensure you have a public DNS entry pointing to the webhook receiver’s IP. Example DNS record:

```
webhook.yourdomain.com -> 192.168.1.100
```

This allows Alertmanager to send alerts using `http://webhook.yourdomain.com:9099/`.

> IPs won't work! Kubernetes needs FQDNs.


## OpenShift Alertmanager Configuration

Modify the Alertmanager configuration to use the webhook receiver. Apply the following YAML to your OpenShift cluster:

```yaml
receivers:
  - name: "webhook-receiver"
    webhook_configs:
      - url: "http://webhook.yourdomain.com:9099/"
```


## Testing the Webhook

To manually test the webhook, send a test alert using `curl`:

```sh
curl -X POST "http://webhook.yourdomain.com:9099/" \
     -H "Content-Type: application/json" \
     -d '{"alert": "Test Alert", "severity": "critical"}'
```


## Continuous Testing

If you're doing troubleshooting or tuning to trigger alerts, using a loop command can be useful. One of the ways I use to refine the alertmanager setup is to generate alerts in series. Take a look at the following example:

1. **Install words command**

```sh
$ yum -y install words
```

2. **Send continuous test alerts**

```sh
#!/bin/bash

while true; do
    NAME=$(shuf -n 1 /usr/share/dict/words)
    sleep 2
    DATE=$(date -u +"%Y-%m-%dT%H:%M:%S%:z")
    oc -n openshift-monitoring exec alertmanager-main-0 -- amtool alert add \
        --alertmanager.url http://localhost:9093 \
        alertname="$NAME" \
        --start="$DATE" \
        severity=critical \
        --annotation=summary="This is a dummy alert with a custom summary"
    sleep 60
done

```

Depending on the version of OpenShift, you may need to scape quotes. Like this:

From:

```sh
--annotation=summary="This is dummy alert with a custom summary"
```

To:

```sh
--annotation="summary=\"This is dummy alert with a custom summary\""
```

In the new command, the summary annotation is enclosed in escaped double quotes (\"...\"). This is necessary in some cases to ensure the argument is correctly parsed as a string by `amtool`.


## Example of the alert received in the webhook

```
Alert received:
 {'receiver': 'Python Fake', 'status': 'firing', 'alerts': [{'status': 'firing', 'labels': {'alertname': 'ireful', 'severity': 'info'}, 'annotations': {'summary': 'This is dummy alert with a custom summary'}, 'startsAt': '2025-03-28T20:19:45Z', 'endsAt': '0001-01-01T00:00:00Z', 'generatorURL': '', 'fingerprint': '4724e6df27b318d6'}], 'groupLabels': {}, 'commonLabels': {'alertname': 'ireful', 'severity': 'info'}, 'commonAnnotations': {'summary': 'This is dummy alert with a custom summary'}, 'externalURL': 'https://console-openshift-console.apps.example.domain.com/monitoring', 'version': '4', 'groupKey': '{}/{severity="info"}:{}', 'truncatedAlerts': 0}
X.X.X.X - - [28/Mar/2025 17:20:48] "POST / HTTP/1.1" 200 -
```


## Alert Severity Levels

Alertmanager supports different severity levels to categorize alerts. The severity level determines the urgency and potential impact of an alert.

| **Severity**  | **Description**                                       | **Use Case** |
|--------------|---------------------------------------------------|------------|
| `info`       | Informational alert, no immediate action needed. | General monitoring, logging events. |
| `warning`    | Potential issue detected, requires attention.     | High memory usage, slow response times. |
| `critical`   | Major failure, immediate action required.         | Service down, database unreachable. |
| `emergency`  | System-wide failure, urgent intervention needed.  | Security breach, data corruption. |

> **Note:** Severity levels can be customized based on your Alertmanager configuration and business requirements.


## Conclusion

This webhook receiver provides a simple way to validate Alertmanager alerts from OpenShift. You can extend it to log alerts, trigger additional actions, or integrate it with monitoring tools.

For issues or contributions, feel free to submit a pull request!
