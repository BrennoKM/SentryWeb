# SentryK8s

Sistema de monitoramento de serviços com mensagens automáticas via RabbitMQ, usando Kubernetes + Helm + CI/CD com GitHub Actions + ArgoCD.

## 📁 Estrutura do Projeto

.
├── src/                # Código fonte da aplicação
│   ├── main.py
│   ├── config.py
│   ├── monitor/
│   ├── messaging/
│   └── utils/
├── helm/               # Helm Chart do projeto
│   └── sentryk8s/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── .github/            # CI com GitHub Actions
│   └── workflows/
├── README.md

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
