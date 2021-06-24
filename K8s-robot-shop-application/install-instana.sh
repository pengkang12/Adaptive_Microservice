helm uninstall instana-agent --namespace instana-agent


#!/bin/bash

helm install instana-agent \
--repo https://agents.instana.io/helm \
--namespace instana-agent \
--create-namespace \
--set agent.key=kp51prMhS1i8-7FVa6GR9g \
--set agent.endpointHost=ingress-orange-saas.instana.io \
--set agent.endpointPort=443 \
--set cluster.name='robot-shop' \
--set zone.name='' \
instana-agent
