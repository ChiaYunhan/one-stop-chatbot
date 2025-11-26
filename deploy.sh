#!/bin/bash

set -e  # Exit on any error

PROJECT_NAME="chatbot"  # Update this to match your PROJECT_NAME from environment.py

# Parse command line arguments
ALLOWED_IP=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --ip)
      ALLOWED_IP="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--ip YOUR_IP_ADDRESS]"
      echo "Example: $0 --ip 203.0.113.25/32"
      exit 1
      ;;
  esac
done

echo "🚀 Starting deployment process..."

if [ -n "$ALLOWED_IP" ]; then
  echo "🔒 Frontend will be restricted to IP: $ALLOWED_IP"
else
  echo "⚠️  Warning: No IP restriction specified. Frontend will be publicly accessible."
  echo "   To restrict access, use: $0 --ip YOUR_IP_ADDRESS/32"
fi

# Step 1: Deploy all stacks except frontend
echo "📦 Deploying backend stacks..."
cd chatbot/backend
cdk deploy \
  "${PROJECT_NAME}-S3Stack" \
  "${PROJECT_NAME}-RoleStack" \
  "${PROJECT_NAME}-LayerStack" \
  "${PROJECT_NAME}-BedrockStack" \
  "${PROJECT_NAME}-ApiGatewayStack" \
  --exclusively \
  --require-approval never

# Step 2: Extract API Gateway URL from CloudFormation outputs
echo "🔍 Extracting API Gateway URL..."
API_URL=$(aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-ApiGatewayStack" \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
  --output text)

if [ -z "$API_URL" ]; then
  echo "❌ Error: Could not find API URL in stack outputs"
  echo "Available outputs:"
  aws cloudformation describe-stacks \
    --stack-name "${PROJECT_NAME}-ApiGatewayStack" \
    --query 'Stacks[0].Outputs[*].{Key:OutputKey,Value:OutputValue}' \
    --output table
  exit 1
fi

echo "✅ Found API URL: $API_URL"

# Step 3: Deploy frontend with the actual API URL using separate app
echo "🌐 Deploying frontend stack with API URL..."
if [ -n "$ALLOWED_IP" ]; then
  cdk deploy "${PROJECT_NAME}-FrontendStack" \
    --app "python frontend_app.py" \
    -c api_url="$API_URL" \
    -c allowed_ip="$ALLOWED_IP" \
    --require-approval never
else
  cdk deploy "${PROJECT_NAME}-FrontendStack" \
    --app "python frontend_app.py" \
    -c api_url="$API_URL" \
    --require-approval never
fi

# Step 4: Get website URL
WEBSITE_URL=$(aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-FrontendStack" \
  --query 'Stacks[0].Outputs[?OutputKey==`WebsiteUrl`].OutputValue' \
  --output text)

echo "🎉 Deployment completed successfully!"
echo "📱 API URL: $API_URL"
echo "🌍 Website URL: $WEBSITE_URL"