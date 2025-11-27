# Resources

## API Gateway

| Resource Name | Description |
|---|---|
| chatbot-RestApi | RESTful API Gateway for all backend operations |

## Lambda Functions

| Function Name | Description |
|---|---|
| chatbot-ListDocuments | Retrieve all documents with status information |
| chatbot-GenerateUploadDocumentLink | Create presigned URLs for secure file uploads |
| chatbot-GenerateDownloadDocumentLink | Generate presigned URLs for document viewing/downloading |
| chatbot-TriggerIngestDocumentsKnowledgeBase | Sync knowledge base after document uploads |
| chatbot-DeleteDocuments | Remove documents from S3 and knowledge base |
| chatbot-QueryKnowledgeBase | Process chat queries using RAG |

## S3 Buckets

| Name  | Description  |
|---|---|
| chatbot-websitebucket-* | Frontend React application hosting (static website) |
| chatbot-document-bucket-{accountId} | Stores all files for the knowledge base |
| chatbot-vector-bucket | Stores vectors for the document bucket (S3 Vectors) |

## Bedrock

| Resource Type | Name/Model | Description |
|---|---|---|
| Knowledge Base | chatbot-knowledge-base-{accountId} | Managed RAG service for document retrieval |
| Foundation Model | amazon.nova-lite-v1:0 | AI model for generating chat responses |
| Embeddings Model | amazon.titan-embed-text-v2:0 | Text embeddings for document indexing |

## IAM Roles

| Role Name | Description |
|---|---|
| chatbot-ApiLambdaRole | Lambda execution role with least-privilege permissions for S3 and Bedrock operations |
| chatbot-BedrockKnowledgeBaseRole | Service role for Bedrock Knowledge Base to access S3 |

## Lambda Layers

| Layer Name | Description |
|---|---|
| chatbot-Layer | Shared dependencies and utilities for Lambda functions |