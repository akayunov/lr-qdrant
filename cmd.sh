#!/bin/bash

set -e

# Функция для сборки контейнеров
build() {
    echo "Сборка контейнеров..."
    docker compose -f docker-compose.yml build
}

# Функция для старта контейнеров
start() {
    echo "Запуск контейнеров..."
    docker compose -f docker-compose.yml up -d

}

stop() {
    if [ "$1" = "-v" ]; then
        echo "Остановка и удаление контейнеров (включая volumes)..."
        docker compose -f docker-compose.yml down -v --timeout 0
    else
        echo "Остановка и удаление контейнеров..."
        docker compose -f docker-compose.yml down --timeout 0
    fi
}

test() {
    docker compose exec -it qdrant-test bash --rcfile /venv/bin/activate
}

# Обработка переданного аргумента
case "$1" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop "${@:2}"
        ;;
    test)
        test
        ;;
    *)
        echo "Использование: $0 {build|start|stop|test}"
        exit 1
        ;;
esac
