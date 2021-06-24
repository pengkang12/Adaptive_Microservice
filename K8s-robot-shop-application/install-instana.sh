kubectl create namespace instana-agent && \
helm install instana-agent --namespace instana-agent \
--repo https://agents.instana.io/helm \
--set agent.key='RT65rPOYSemNpWaVAfcIEg' \
--set agent.endpointHost='ingress-orange-saas.instana.io' \
--set cluster.name='microservices' \
--set zone.name='' \
instana-agent
