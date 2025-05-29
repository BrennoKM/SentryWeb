FROM rabbitmq:3.12-management

RUN apt-get update && apt-get install -y curl unzip && \
    curl -L -o /plugins/rabbitmq_delayed_message_exchange-3.12.0.ez https://github.com/rabbitmq/rabbitmq-delayed-message-exchange/releases/download/v3.12.0/rabbitmq_delayed_message_exchange-3.12.0.ez && \
    chmod 644 /plugins/rabbitmq_delayed_message_exchange-3.12.0.ez

ENV RABBITMQ_ENABLED_PLUGINS_FILE=/etc/rabbitmq/enabled_plugins

RUN echo '[rabbitmq_management, rabbitmq_delayed_message_exchange].' > /etc/rabbitmq/enabled_plugins
