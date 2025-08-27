# SentryWeb

<p align="justify">
Um sistema distribuído, escalável e resiliente para agendamento e processamento de tarefas genéricas, desenvolvido como Trabalho de Conclusão de Curso (TCC) em Ciência da Computação. Embora o protótipo valide o conceito através do monitoramento de serviços web (<i>health checks</i>), a arquitetura foi projetada para ser uma plataforma flexível, capaz de suportar diversos tipos de trabalhos em um ambiente de alta performance.
</p>

---
## 🎯 O Problema e a Solução

<p align="justify">
No cenário atual de microsserviços, a necessidade de executar tarefas agendadas, que vão desde verificações de disponibilidade até processamento de dados e envio de relatórios, é onipresente. No entanto, a construção de um agendador que seja ao mesmo tempo <strong>escalável</strong> (capaz de lidar com milhares de tarefas) e <strong>resiliente</strong> (tolerante a falhas de nós individuais) é um desafio de engenharia complexo.
</p>

<p align="justify">
O <b>SentryWeb</b> foi projetado para resolver esse problema. Utilizando uma arquitetura de microsserviços orquestrada com <strong>Kubernetes</strong> e desacoplada por um <i>message broker</i> <strong>RabbitMQ</strong>, o sistema oferece uma plataforma robusta para o agendamento e a execução de qualquer tipo de tarefa. A solução é nativa da nuvem, projetada para ser gerenciada por ferramentas de GitOps como o <strong>ArgoCD</strong> e monitorada opcionalmente pelo <strong>Prometheus</strong>, garantindo que, mesmo com o aumento da carga ou a falha de componentes, as tarefas sejam distribuídas e processadas de forma eficiente e confiável.
</p>

---
## ✨ Funcionalidades Principais

* **Plataforma de Tarefas Genéricas:** A arquitetura é extensível, permitindo a criação de diferentes tipos de `workers` para executar qualquer operação, bastando definir um `task_type` e um `payload` correspondente.
* **Agendamento Distribuído e Resiliente:** Múltiplas instâncias do `Scheduler` podem rodar em paralelo. As tarefas são distribuídas entre eles usando um algoritmo de hash consistente, garantindo que não haja um ponto único de falha.
* **Processamento Paralelo e Escalável:** O `Worker` é um serviço *stateless* que processa tarefas em paralelo usando um pool de threads, permitindo o processamento de um grande volume de mensagens.
* **Autoescalonamento Inteligente (HPA):** O sistema utiliza o Horizontal Pod Autoscaler do Kubernetes com duas estratégias:
    * **Scheduler:** Escala com base em métricas de CPU/Memória, ideal para um serviço *stateful*.
    * **Worker:** Escala com base em **métricas de negócio customizadas** (mensagens na fila do RabbitMQ), uma abordagem muito mais eficiente que o simples uso de CPU para cargas de trabalho I/O-bound.
* **Comunicação Assíncrona e Desacoplada:** O uso do RabbitMQ garante que `Schedulers` e `Workers` operem de forma independente, aumentando a resiliência e a flexibilidade do sistema.
* **Sincronização Dinâmica:** Os `Schedulers` se mantêm sincronizados em tempo real, detectando novas tarefas e mudanças no número de réplicas sem a necessidade de reinicialização.

---
## 🏛️ Arquitetura e Fluxo de Funcionamento

<p align="justify">
O SentryWeb opera com base em uma arquitetura de microsserviços, onde cada componente tem uma responsabilidade clara e se comunica de forma assíncrona.
</p>

1.  **Inserção de Tarefas:** Um script (`insert_task.py`) insere uma nova tarefa no banco de dados **PostgreSQL** e publica uma notificação em uma *exchange* do tipo `fanout` no **RabbitMQ**.
2.  **Sincronização dos Schedulers:** Todas as instâncias ativas do **Scheduler Service** recebem a notificação da nova tarefa. Cada uma aplica um algoritmo de hash (`task_uuid % total_schedulers`) para determinar qual delas é a "dona" da tarefa. O Scheduler responsável a adiciona à sua fila de prioridade interna (um *min-heap* baseado em tempo).
3.  **Agendamento:** O `Scheduler` "dono" da tarefa aguarda o momento certo e publica a tarefa em uma fila de trabalho (`tasks`) no RabbitMQ.
4.  **Processamento pelos Workers:** Uma instância disponível do **Worker Service** consome a mensagem da fila `tasks`. O Worker utiliza um `ThreadPoolExecutor` para processar múltiplas tarefas concorrentemente.
5.  **Execução:** A thread do Worker executa a operação definida (no caso do protótipo, um *health check* de URL) e, ao final, envia um `ACK` para o RabbitMQ, confirmando que a tarefa foi concluída com sucesso.
6.  **Orquestração e Escalabilidade:** Todo o sistema é conteinerizado com **Docker** e implantado no **Kubernetes**. O HPA monitora a carga de trabalho (CPU no Scheduler, mensagens na fila para o Worker) e ajusta o número de réplicas de cada serviço automaticamente.

---
## 🛠️ Tecnologias Utilizadas

* **Backend:** Python
* **Orquestração:** Kubernetes, Docker, Helm
* **Mensageria:** RabbitMQ
* **Banco de Dados:** PostgreSQL
* **CI/CD:** GitHub Actions (CI), ArgoCD (CD)
* **Monitoramento:** Prometheus, Grafana
* **Infraestrutura:** Manifests YAML para Kubernetes

---
## 🚀 Como Executar o Projeto

<p align="justify">
Para executar o SentryWeb, é necessário ter um ambiente com Docker e Kubernetes (como Minikube ou Docker Desktop) configurado, além do Helm.
</p>

### 1. Clone o repositório:
```bash
git clone [https://github.com/BrennoKM/SentryWeb.git](https://github.com/BrennoKM/SentryWeb.git)
```

### 2. Configure os Pré-requisitos
<p align="justify">
Antes de implantar a aplicação, é necessário criar os segredos e as configurações iniciais do banco de dados no seu cluster.
</p>

```bash
# Crie os segredos para RabbitMQ e PostgreSQL
kubectl apply -f deploy/secrets/

# Crie o ConfigMap com o script de inicialização do banco
kubectl apply -f deploy/configmap/
```

### 3. Implante a Aplicação com Helm
<p align="justify">
O projeto utiliza um Helm Chart para gerenciar a implantação de todos os componentes (Scheduler, Worker) e suas dependências (PostgreSQL, RabbitMQ).
</p>

```bash
# Navegue até o diretório do chart
cd deploy/helm/sentryk8s

# Instale o chart no seu cluster
helm install sentryweb . --namespace sentryk8s --create-namespace
```

### 4. Insira Tarefas de Teste
<p align="justify">
Após a implantação, utilize os scripts na pasta `src/scripts` para popular o banco de dados com tarefas de monitoramento.
</p>

```bash
# Exemplo de como executar o script (requer conexão com o DB)
python src/scripts/insert_tasks_from_json.py
```

---
## 🔮 Futuras Melhorias

* **API de Gerenciamento:** Desenvolver um serviço de API (ex: em Flask ou FastAPI) para gerenciar o CRUD de tarefas de forma programática, em vez de usar scripts.
* **Dashboard de Visualização:** Criar uma interface web (frontend) para visualizar o status dos serviços em tempo real e o histórico de execuções.
* **Workers Especializados:** Implementar novos tipos de `workers` para executar outras tarefas, como envio de e-mails, processamento de imagens ou ETLs simples.
* **Métricas Detalhadas:** Coletar e expor métricas de tempo de resposta (latência) de cada serviço monitorado.
