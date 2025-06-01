# SentryK8s

Sistema de monitoramento de serviços com mensagens automáticas via RabbitMQ, usando Kubernetes + Helm + CI/CD com GitHub Actions + ArgoCD.

## 📁 Estrutura do Projeto

.<br>
├── deploy<br>
│   ├── argocd<br>
│   │   ├── cd.yaml<br>
│   │   ├── image-updater-rbac.yaml<br>
│   │   └── values.yaml<br>
│   └── helm<br>
│       └── sentryk8s<br>
│           ├── Chart.lock<br>
│           ├── charts<br>
│           │   ├── postgresql-12.1.0.tgz<br>
│           │   └── rabbitmq-12.0.0.tgz<br>
│           ├── Chart.yaml<br>
│           ├── templates<br>
│           │   ├── deployment-worker.yaml<br>
│           │   ├── _helpers.tpl<br>
│           │   ├── _NOTES.txt<br>
│           │   ├── service-scheduler.yaml<br>
│           │   ├── service-worker.yaml<br>
│           │   ├── statefulset-scheduler.yaml<br>
│           │   └── tests<br>
│           └── values.yaml<br>
├── imagens<br>
│   └── arquitetura.png<br>
├── readme.md<br>
└── src<br>

## 🚀 Como rodar com Helm (local com Minikube)

helm install sentryk8s ./helm/sentryk8s

Para atualizar após mudanças:

helm upgrade sentryk8s ./helm/sentryk8s

## ⚙️ Tecnologias

- Python 3
- RabbitMQ
- Kubernetes (Minikube)
- Helm
- GitHub Actions
- ArgoCD (CD)

## 📦 Estrutura da Aplicação (src/)

./src<br>
├── db<br>
│   ├── database.py<br>
│   └── tasks.py<br>
├── messaging<br>
│   ├── consumer.py<br>
│   ├── emitter.py<br>
│   ├── producer.py<br>
├── rabbitmq<br>
│   └── Dockerfile<br>
├── scheduler<br>
│   ├── Dockerfile<br>
│   ├── main.py<br>
│   └── requirements.txt<br>
├── scripts<br>
│   ├── insert_task.py<br>
│   ├── resetdb.sql<br>
│   └── test_hash.py<br>
└── worker<br>
    ├── Dockerfile<br>
    ├── main.py<br>
    ├── monitor<br>
    └── requirements.txt<br>

## 📌 Objetivo

Monitorar serviços essenciais (como APIs ou banco de dados) e emitir mensagens para uma fila RabbitMQ caso algo esteja errado. Isso permite a automação de alertas ou abertura de chamados.