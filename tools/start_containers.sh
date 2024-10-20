#!/usr/bin/bash

CONTAINER_NAME="university_domains_list_api_app"
DOCKER_FILE="docker-compose.yml"

docker compose stop
docker compose -f ${DOCKER_FILE} rm --force
docker compose -f ${DOCKER_FILE} build
docker compose -f ${DOCKER_FILE} up -d --remove-orphans
