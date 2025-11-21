#!/bin/bash
set -e

PROJECT_NAME="chatbot"  # Update this to match your PROJECT_NAME

cd chatbot/backend

echo "🗑️  Starting cleanup process..."

# Function to empty S3 bucket if it exists
empty_bucket() {
    local stack_name=$1
    local bucket_name=$(aws cloudformation describe-stack-resources \
        --stack-name "$stack_name" \
        --query 'StackResources[?ResourceType==`AWS::S3::Bucket`].PhysicalResourceId' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$bucket_name" ] && [ "$bucket_name" != "None" ]; then
        echo "📦 Found bucket in $stack_name: $bucket_name"
        echo "🗑️ Emptying bucket..."
        
        # Empty the bucket (remove all objects and versions)
        aws s3 rm s3://$bucket_name --recursive 2>/dev/null || true
        
        # Remove any versioned objects if versioning is enabled
        aws s3api list-object-versions --bucket $bucket_name --query 'Versions[].{Key:Key,VersionId:VersionId}' --output text 2>/dev/null | while read key version; do
            if [ -n "$key" ] && [ -n "$version" ] && [ "$key" != "None" ] && [ "$version" != "None" ]; then
                aws s3api delete-object --bucket $bucket_name --key "$key" --version-id "$version" 2>/dev/null || true
            fi
        done
        
        # Remove any delete markers
        aws s3api list-object-versions --bucket $bucket_name --query 'DeleteMarkers[].{Key:Key,VersionId:VersionId}' --output text 2>/dev/null | while read key version; do
            if [ -n "$key" ] && [ -n "$version" ] && [ "$key" != "None" ] && [ "$version" != "None" ]; then
                aws s3api delete-object --bucket $bucket_name --key "$key" --version-id "$version" 2>/dev/null || true
            fi
        done
        
        echo "✅ Bucket $bucket_name emptied"
    fi
}

echo "Destroying stacks in reverse order..."

# Destroy frontend first (empty bucket first)
echo "Destroying frontend stack..."
empty_bucket "${PROJECT_NAME}-FrontendStack"
cdk destroy "${PROJECT_NAME}-FrontendStack" --app "python frontend_app.py" --force || true

# Destroy API Gateway stack
echo "Destroying API Gateway stack..."
cdk destroy "${PROJECT_NAME}-ApiGatewayStack" --force || true

# Destroy Bedrock stack
echo "Destroying Bedrock stack..."
cdk destroy "${PROJECT_NAME}-BedrockStack" --force || true

# Destroy Lambda Layer stack
echo "Destroying Lambda Layer stack..."
cdk destroy "${PROJECT_NAME}-LayerStack" --force || true

# Destroy IAM roles stack
echo "Destroying IAM roles stack..."
cdk destroy "${PROJECT_NAME}-RoleStack" --force || true

# Destroy S3 stack last (empty buckets first)
echo "Destroying S3 stack..."
empty_bucket "${PROJECT_NAME}-S3Stack"
cdk destroy "${PROJECT_NAME}-S3Stack" --force || true

echo "🎉 Cleanup completed!"