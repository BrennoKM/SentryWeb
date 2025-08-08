# SentryK8s

Um sistema distribuído, escalável e resiliente para agendamento e execução de tarefas, com foco no monitoramento da disponibilidade de serviços web. O projeto utiliza uma arquitetura de microsserviços orquestrada pelo Kubernetes e desacoplada pelo RabbitMQ.

---

## 🎯 Sobre o Projeto

O SentryK8s foi desenvolvido para resolver o desafio de monitorar continuamente a saúde de múltiplos serviços em um ambiente distribuído. A plataforma é composta por dois microsserviços principais:

* **Scheduler:** Um serviço *stateful* e distribuído, responsável por determinar *quais* e *quando* as tarefas devem ser executadas. Ele utiliza um algoritmo de particionamento (sharding) para garantir que não haja um ponto único de falha.
* **Worker:** Um serviço *stateless* e concorrente, responsável pela execução real das tarefas. Ele foi projetado para escalar horizontalmente e processar um grande volume de verificações em paralelo.

Um dos diferenciais do projeto é a sua **estratégia de autoescalonamento inteligente**. Através de experimentos, foi constatado que métricas de recursos tradicionais (como CPU) são ineficazes para este tipo de carga de trabalho. A solução implementada utiliza métricas de negócio customizadas, extraídas diretamente do RabbitMQ, permitindo que o sistema se adapte de forma precisa e eficiente à carga real de trabalho.

---

## ⚙️ Tecnologias Utilizadas

* **Linguagem:** Python 3
* **Orquestração:** Kubernetes (Minikube para desenvolvimento local)
* **Mensageria:** RabbitMQ
* **Banco de Dados:** PostgreSQL
* **Empacotamento:** Helm
* **CI/CD:** GitHub Actions (CI) e ArgoCD (GitOps para CD)
* **Monitoramento:** Prometheus e Prometheus Adapter

---

## 📁 Estrutura do Projeto

A estrutura do repositório está organizada da seguinte forma:

```
.
├── deploy/              # Manifestos de deployment e configuração
│   ├── argocd/          # Aplicações do ArgoCD
│   └── helm/sentryk8s/  # Chart Helm principal da aplicação
├── src/                 # Código-fonte da aplicação
│   ├── scheduler/       # Código do microsserviço Scheduler
│   └── worker/          # Código do microsserviço Worker
└── .github/workflows/   # Pipeline de CI com GitHub Actions
```

---

## 🚀 Como Rodar Localmente (com Minikube)

**Pré-requisitos:**

* Minikube
* Helm
* kubectl

**1. Inicie o Minikube:**

```bash
minikube start
```

**2. Instale a Aplicação com Helm:**

Navegue até a raiz do projeto e execute o comando de instalação. O Helm irá implantar o SentryK8s e suas dependências (PostgreSQL e RabbitMQ).

```bash
helm install sentryk8s ./deploy/helm/sentryk8s
```

**3. Para atualizar após mudanças no código:**

Para atualizar a implantação, basta usar o comando de upgrade do Helm:

```bash
helm upgrade sentryk8s ./deploy/helm/sentryk8s
```

**4. Fluxo CI/CD (opcional):**

Para consilidar o fluxo CI/CD é necessário configurar os manifestos do ArgoCD com os repositórios corretos.
