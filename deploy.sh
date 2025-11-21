#!/bin/bash

set -e  # Exit on any error

PROJECT_NAME="chatbot"  # Update this to match your PROJECT_NAME from environment.py

echo "🚀 Starting deployment process..."

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
cdk deploy "${PROJECT_NAME}-FrontendStack" \
  --app "python frontend_app.py" \
  -c api_url="$API_URL" \
  --require-approval never

# Step 4: Get website URL
WEBSITE_URL=$(aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-FrontendStack" \
  --query 'Stacks[0].Outputs[?OutputKey==`WebsiteUrl`].OutputValue' \
  --output text)

echo "🎉 Deployment completed successfully!"
echo "📱 API URL: $API_URL"
echo "🌍 Website URL: $WEBSITE_URL"