#!/bin/bash

# AWS Deployment Script for Soft Skills Practice API

set -e

# Configuration
PROJECT_NAME="soft-skills-practice-api"
AWS_REGION="us-east-1"
ENVIRONMENT="production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting AWS Deployment for ${PROJECT_NAME}${NC}"

# Check prerequisites
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not found. Please install AWS CLI first.${NC}"
    exit 1
fi

# Check Terraform
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform not found. Please install Terraform first.${NC}"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Build and push Docker image
echo -e "${YELLOW}🏗️ Building and pushing Docker image...${NC}"

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_NAME="${PROJECT_NAME}"
IMAGE_TAG="latest"
FULL_IMAGE_NAME="${ECR_REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

# Create ECR repository if it doesn't exist
echo -e "${BLUE}📦 Creating ECR repository...${NC}"
aws ecr describe-repositories --repository-names ${IMAGE_NAME} --region ${AWS_REGION} 2>/dev/null || \
aws ecr create-repository --repository-name ${IMAGE_NAME} --region ${AWS_REGION}

# Login to ECR
echo -e "${BLUE}🔐 Logging into ECR...${NC}"
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Build Docker image
echo -e "${BLUE}🏗️ Building Docker image...${NC}"
docker build -f Dockerfile.prod -t ${FULL_IMAGE_NAME} .

# Push Docker image
echo -e "${BLUE}📤 Pushing Docker image to ECR...${NC}"
docker push ${FULL_IMAGE_NAME}

echo -e "${GREEN}✅ Docker image pushed successfully${NC}"

# Deploy infrastructure with Terraform
echo -e "${YELLOW}🏗️ Deploying infrastructure with Terraform...${NC}"

cd infrastructure/terraform

# Initialize Terraform
echo -e "${BLUE}🔧 Initializing Terraform...${NC}"
terraform init

# Plan deployment
echo -e "${BLUE}📋 Planning Terraform deployment...${NC}"
terraform plan -var="aws_region=${AWS_REGION}" -var="environment=${ENVIRONMENT}" -var="project_name=${PROJECT_NAME}"

# Apply deployment
echo -e "${BLUE}🚀 Applying Terraform deployment...${NC}"
terraform apply -var="aws_region=${AWS_REGION}" -var="environment=${ENVIRONMENT}" -var="project_name=${PROJECT_NAME}" -auto-approve

# Get outputs
API_GATEWAY_URL=$(terraform output -raw api_gateway_url)
LOAD_BALANCER_DNS=$(terraform output -raw load_balancer_dns)

echo -e "${GREEN}✅ Infrastructure deployed successfully${NC}"

# Wait for application to be ready
echo -e "${YELLOW}⏳ Waiting for application to be ready...${NC}"

# Wait for load balancer to be healthy
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -f -s "http://${LOAD_BALANCER_DNS}/health/" > /dev/null; then
        echo -e "${GREEN}✅ Application is healthy${NC}"
        break
    else
        echo -e "${BLUE}⏳ Waiting for application... (attempt $((attempt+1))/$max_attempts)${NC}"
        sleep 30
        attempt=$((attempt+1))
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo -e "${RED}❌ Application health check failed after $max_attempts attempts${NC}"
    exit 1
fi

# Test API endpoints
echo -e "${YELLOW}🧪 Testing API endpoints...${NC}"

# Test through API Gateway
echo -e "${BLUE}Testing API Gateway endpoint...${NC}"
if curl -f -s "${API_GATEWAY_URL}/health/" > /dev/null; then
    echo -e "${GREEN}✅ API Gateway health check passed${NC}"
else
    echo -e "${RED}❌ API Gateway health check failed${NC}"
fi

# Test soft skills endpoint
echo -e "${BLUE}Testing soft skills endpoint...${NC}"
if curl -f -s "${API_GATEWAY_URL}/soft-skills/" > /dev/null; then
    echo -e "${GREEN}✅ Soft skills endpoint working${NC}"
else
    echo -e "${RED}❌ Soft skills endpoint failed${NC}"
fi

# Populate initial data
echo -e "${YELLOW}📚 Populating initial data...${NC}"

# Get one of the EC2 instance IPs to run the data population script
INSTANCE_ID=$(aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=${PROJECT_NAME}-instance" "Name=instance-state-name,Values=running" \
    --query 'Reservations[0].Instances[0].InstanceId' \
    --output text \
    --region ${AWS_REGION})

if [ "$INSTANCE_ID" != "None" ] && [ "$INSTANCE_ID" != "" ]; then
    echo -e "${BLUE}Running data population on instance ${INSTANCE_ID}...${NC}"
    aws ssm send-command \
        --instance-ids ${INSTANCE_ID} \
        --document-name "AWS-RunShellScript" \
        --parameters 'commands=["cd /opt/soft-skills-api && docker-compose exec -T api python scripts/populate_data.py"]' \
        --region ${AWS_REGION} > /dev/null
    
    echo -e "${GREEN}✅ Initial data population started${NC}"
else
    echo -e "${YELLOW}⚠️ No running instances found, skipping data population${NC}"
fi

# Display deployment information
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Information:${NC}"
echo -e "${BLUE}=========================${NC}"
echo -e "${BLUE}🌐 API Gateway URL:${NC} ${API_GATEWAY_URL}"
echo -e "${BLUE}🔧 Load Balancer:${NC} http://${LOAD_BALANCER_DNS}"
echo -e "${BLUE}📚 API Documentation:${NC} ${API_GATEWAY_URL}/docs"
echo -e "${BLUE}🩺 Health Check:${NC} ${API_GATEWAY_URL}/health/"
echo ""
echo -e "${BLUE}🔗 Quick Test Commands:${NC}"
echo -e "${BLUE}curl ${API_GATEWAY_URL}/health/${NC}"
echo -e "${BLUE}curl ${API_GATEWAY_URL}/soft-skills/${NC}"
echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo -e "1. Configure your domain name to point to the API Gateway"
echo -e "2. Set up SSL certificate for HTTPS"
echo -e "3. Configure monitoring and alerting"
echo -e "4. Set up backup strategy for RDS"
echo ""
echo -e "${GREEN}🚀 Your Soft Skills Practice API is now live!${NC}"

cd ../..

exit 0
