#!/usr/bin/env bash

set -euo pipefail

APP_DIR="/home/ubuntu/healthbot"

cd "$APP_DIR"

echo "==> Logging in to ECR"

AWS_ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
AWS_REGION="ap-south-1"

BACKEND_ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/healthbot-backend"
FRONTEND_ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/healthbot-frontend"

aws ecr get-login-password --region "$AWS_REGION" \
  | sudo docker login \
      --username AWS \
      --password-stdin \
      "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

echo "==> Pulling latest backend image"

sudo docker pull "${BACKEND_ECR_URI}:latest"

echo "==> Pulling latest frontend image"

sudo docker pull "${FRONTEND_ECR_URI}:latest"

echo "==> Starting production stack"

sudo docker compose \
  -f docker-compose.prod.yml \
  up -d

echo "==> Removing unused Docker images"

sudo docker image prune -f

echo "==> Waiting for application"

sleep 10

echo "==> Checking application health"

curl --fail --silent --show-error \
  https://3.110.78.125.nip.io/health

echo

echo "==> Deployment successful"
