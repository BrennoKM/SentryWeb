# SentryK8s

Sistema de monitoramento de serviços com mensagens automáticas via RabbitMQ, usando Kubernetes + Helm + CI/CD com GitHub Actions + ArgoCD.

## 📁 Estrutura do Projeto

.
├── helm
│   └── sentryk8s
│       ├── charts
│       ├── Chart.yaml
│       ├── templates
│       │   ├── deployment.yaml
│       │   ├── _helpers.tpl
│       │   ├── hpa.yaml
│       │   ├── ingress.yaml
│       │   ├── NOTES.txt
│       │   ├── serviceaccount.yaml
│       │   ├── service.yaml
│       │   └── tests
│       │       └── test-connection.yaml
│       └── values.yaml
├── README.md
└── src
    ├── messaging
    ├── scheduler
    └── worker

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

src/
├── main.py             # Entrada principal
├── config.py           # Configurações
├── monitor/            # Módulos de monitoramento
├── messaging/          # Emissor de mensagens
└── utils/              # Funções auxiliares

## 📌 Objetivo

Monitorar serviços essenciais (como APIs ou banco de dados) e emitir mensagens para uma fila RabbitMQ caso algo esteja errado. Isso permite a automação de alertas ou abertura de chamados.