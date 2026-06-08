.PHONY: help build deploy monitor clean

help:
	@echo "Available commands:"
	@echo "  build     - Build Docker image"
	@echo "  deploy    - Deploy to Kind cluster"
	@echo "  monitor   - Port-forward for monitoring"
	@echo "  clean     - Delete all resources"

build:
	docker build -t siarhei0788/lab4-app:web14 .
	C:\tools\kind load docker-image siarhei0788/lab4-app:web14 --name web14-cluster

deploy:
	kubectl apply -f k8s/namespace.yaml
	kubectl apply -f k8s/deployment.yaml
	kubectl apply -f k8s/service.yaml
	kubectl apply -f k8s/servicemonitor.yaml
	kubectl apply -f k8s/prometheusrule.yaml

monitor:
	@echo "Grafana: http://localhost:3000 (admin/admin123)"
	@echo "Prometheus: http://localhost:9090"
	@echo "App metrics: http://localhost:9062/metrics"
	kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80 &
	kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090 &
	kubectl port-forward -n app-monitoring-230489-v14 svc/web14-app 9062:9062 &

clean:
	kubectl delete namespace app-monitoring-230489-v14 --ignore-not-found