# One-Stop RAG Chatbot

A full-stack serverless chatbot application that enables users to upload documents and query them using Retrieval-Augmented Generation (RAG) powered by Amazon Bedrock. Built with React frontend and AWS CDK for infrastructure deployment.

## 🎯 About

This **full-stack serverless** chatbot application is a **quick and easy prototype** designed for learning **full-stack development**, **RAG (Retrieval-Augmented Generation)**, and **AWS cloud development**. The application enables users to upload documents and query them using RAG powered by Amazon Bedrock, leveraging **Amazon Bedrock Knowledge Base** with **S3 Vectors** for cost-effective document retrieval and Amazon Nova Lite model for generating intelligent responses with proper citations. Built with React frontend and AWS CDK for infrastructure deployment.

**⚠️ Important Note**: Chat conversations are session-based only. All chat history will be lost when the page is refreshed or closed.

## 📺 Demo

Watch a walkthrough of the application in action:

![Demo Video](showcase.mp4)

*The demo showcases document upload, knowledge base management, and RAG-powered chat interactions.*

## ✨ Features

- **🤖 RAG-Powered Chat**: Intelligent responses with source citations from your uploaded documents using Amazon Nova Lite
- **📄 Simple Document Upload & Management**: Automatic upload, processing, and management of PDF files using default chunking methods
- **⚡ Serverless Architecture**: Fully serverless with automatic scaling and cost-effective S3 Vectors storage

## 🏗️ Architecture

### Infrastructure Components

| **Component** | **Service** | **Resource Name** | **Description** |
|---------------|-------------|-------------------|----------------|
| **Frontend** | S3 + Static Website | `chatbot-websitebucket-*` | React application with TypeScript |
| **API Gateway** | AWS API Gateway | `chatbot-RestApi` | RESTful APIs for all operations |
| **Compute** | AWS Lambda | 6 Functions (see below) | Serverless functions for all backend logic |
| **Document Storage** | S3 Bucket | `chatbot-document-bucket-{accountId}` | Secure document storage with CORS |
| **Vector Database** | S3 Vectors | `chatbot-vector-bucket` | Cost-effective embeddings storage for RAG |
| **Knowledge Base** | Amazon Bedrock KB | `chatbot-knowledge-base-{accountId}` | Managed RAG service |
| **AI Model** | Amazon Nova Lite | `amazon.nova-lite-v1:0` | Foundation model for chat responses |
| **Embeddings** | Titan Text v2 | `amazon.titan-embed-text-v2:0` | Text embeddings for document indexing |

### Lambda Functions

| **Function** | **Purpose** |
|--------------|-------------|
| `chatbot-ListDocuments` | Retrieve all documents with status information |
| `chatbot-GenerateUploadDocumentLink` | Create presigned URLs for secure file uploads |
| `chatbot-GenerateDownloadDocumentLink` | Generate presigned URLs for document viewing/downloading |
| `chatbot-TriggerIngestDocumentsKnowledgeBase` | Sync knowledge base after document uploads |
| `chatbot-DeleteDocuments` | Remove documents from S3 and knowledge base |
| `chatbot-QueryKnowledgeBase` | Process chat queries using RAG |

## 🔧 Prerequisites

Before deploying this application, ensure you have:

### Required Software
- **Node.js** (v18 or later) and npm
- **Python** (v3.12 or later)
- **AWS CLI** (v2) configured with appropriate credentials
- **AWS CDK** (v2.222.0 or later)
- **Git**

### AWS Account Setup
1. **AWS Account**: Active AWS account with billing enabled
2. **Bedrock Access**: Ensure Amazon Bedrock is available in your deployment region
3. **Service Access**: This system requires access to the following AWS services:
   - Amazon Bedrock (Nova Lite and Titan Embeddings models)
   - AWS Lambda
   - Amazon S3 (including S3 Vectors)
   - Amazon API Gateway
   - AWS IAM
   - AWS CloudFormation

### AWS Credentials
Configure AWS CLI with a user/role that has permissions for:
- CloudFormation (full access)
- S3 (full access)
- Lambda (full access)
- API Gateway (full access)
- Bedrock (full access)
- IAM (role creation and policy attachment)

```bash
aws configure
# or
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## 🚀 Deployment Instructions

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd one-stop-chatbot

# Install Python dependencies (for CDK)
cd chatbot/backend
pip install -r requirements.txt

# Install Node.js dependencies (for frontend)
cd ../frontend
npm install
```

### Step 2: CDK Bootstrap

Bootstrap CDK in your AWS account (one-time setup per region). You can do this via AWS Console or CLI:

#### AWS Console Managments

1. Sign into AWS Management Console with your account.
2. Go to the region you desire to deploy in. (us-east-1 recomended)
3. Enter into AWS CloudShell
4. Enter
```bash
cdk bootstrap <aws://{account id}/{region}
```

### Step 3: Deploy Infrastructure

Deploy all AWS resources using the provided script:

#### Option 1: Deploy with IP Restriction (Recommended for Security)

First, get your current IP address:

```bash
# Get your public IP address
curl ifconfig.me
```

Then deploy with IP restriction to limit frontend access to only your IP:

```bash
# From the project root directory
chmod +x deploy.sh
./deploy.sh --ip YOUR_IP_ADDRESS/32

# Example with actual IP:
# ./deploy.sh --ip 203.0.113.25/32 or 203.0.113.25
```

#### Option 2: Deploy without IP Restriction (Public Access)

```bash
# From the project root directory
chmod +x deploy.sh
./deploy.sh
```

**⚠️ Warning**: Deploying without IP restriction makes the frontend publicly accessible to anyone with the URL.

#### What the deployment script does:
1. Deploy backend infrastructure (S3, Lambda, API Gateway, Bedrock)
2. Extract the API Gateway URL
3. Build and deploy the frontend with the correct API endpoint
4. Optionally restrict frontend S3 bucket access to your IP address
5. Provide you with the final website URL

#### IP Restriction Details:

- The `/32` suffix means exactly one IP address (CIDR notation)
- If your IP changes, redeploy with the new IP: `./deploy.sh --ip NEW_IP/32`
- For multiple IPs or a range, use appropriate CIDR notation (e.g., `/24` for 256 IPs)

### Step 4: Access Your Application

After successful deployment, you'll see output similar to:

```
🎉 Deployment completed successfully!
📱 API URL: https://abc123.execute-api.us-east-1.amazonaws.com/chatbot
🌍 Website URL: http://chatbot-websitebucket-xyz.s3-website-us-east-1.amazonaws.com
```

Visit the Website URL to access your chatbot application.

### Alternative: Manual Deployment

If you prefer manual deployment:

```bash
cd chatbot/backend

# Deploy backend stacks
cdk deploy chatbot-S3Stack chatbot-RoleStack chatbot-LayerStack chatbot-BedrockStack chatbot-ApiGatewayStack --require-approval never

# Get API URL from CloudFormation outputs
aws cloudformation describe-stacks --stack-name chatbot-ApiGatewayStack --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' --output text

# Deploy frontend (replace YOUR_API_URL with actual URL)
cdk deploy chatbot-FrontendStack --app "python frontend_app.py" -c api_url="YOUR_API_URL" --require-approval never
```

## 📖 Usage

### Uploading Documents
1. Click "Upload Files" in the Knowledge Base section
2. Select PDF files (max 15MB each). 
**⚠️ Important Note**: Scanned PDF in which you cant highlight words will not work.
3. Wait for processing to complete (status will show "INDEXED")
4. Use "Sync Knowledge Base" to ensure documents are searchable

### Chatting with Documents
1. Navigate to the Chat section
2. Type questions about your uploaded documents
3. The AI will respond with citations showing which documents were referenced
4. Continue the conversation - context is maintained within each session

### Managing Documents
- **View**: Click any document to preview it in the built-in PDF viewer
- **Delete**: Use "Select" mode to choose and delete multiple documents
- **Status**: Monitor processing status in real-time

## 🧹 Cleanup

To remove all AWS resources and avoid ongoing charges:

```bash
chmod +x cleanup.sh
./cleanup.sh
```

This will safely delete all resources including:
- Emptying S3 buckets before deletion
- Removing all Lambda functions and layers
- Deleting API Gateway and other AWS resources
- Cleaning up IAM roles and policies

## 🛠️ Development

### Project Structure

```
one-stop-chatbot/
├── chatbot/
│   ├── backend/          # AWS CDK infrastructure
│   │   ├── lambda/       # Lambda function code
│   │   ├── stacks/       # CDK stack definitions
│   │   └── app.py        # Main CDK app
│   └── frontend/         # React TypeScript application
│       ├── src/
│       │   ├── features/ # Feature-based components
│       │   └── types/    # TypeScript definitions
│       └── package.json
├── deploy.sh             # Deployment script
├── cleanup.sh            # Cleanup script
└── README.md
```

### Local Development

```bash
# Backend development
cd chatbot/backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend development
cd ../frontend
npm install
npm run dev
```

### Environment Variables

The frontend automatically uses the deployed API URL. For local development, update `chatbot/frontend/src/config.ts`.

## 📋 Cost Considerations

This application uses several AWS services. Estimated costs for light usage:
- **S3 Storage**: ~$0.023/GB/month
- **Lambda**: Free tier covers most usage
- **API Gateway**: ~$3.50 per million requests
- **Bedrock**: Pay per token (Nova Lite is cost-effective)

## 🔧 Troubleshooting

### Common Issues

1. **Bedrock Model Access**: Ensure you have requested access to Nova Lite and Titan Embeddings in the Bedrock console
2. **Region Availability**: Use us-east-1 for best Bedrock model and service availability
3. **Bootstrap Issues**: Run `cdk bootstrap` if you see deployment errors
4. **File Upload Fails**: Check file size (15MB limit) and format (PDF only)


## 📺 Demo Video

*Coming soon - A complete walkthrough of deployment and usage*

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

This is a personal learning project to explore full-stack development, RAG, and AWS technologies.

---

Built with ❤️ using AWS CDK, React, and Amazon Bedrock
