# Resources

## API

| API | Lambda | Description |
| ----| ---- | ---- |
| - | GenerateDownloadS3Link | API to download file from s3 bucket (should be used in pdf viewer as well) |
| - | GenerateUploadDocumentLink | API for users to upload document to be ingested into s3 bucket to be ingested into knowledge base |
| - | GetDocuments | API to get list of all documents in s3 bucket/knowledge base|
| - | DeleteDocuments | API to delete documents in s3 bucket and no longer part of knowledge base |
| - | SendUserChat | API to send user chat to bedrock to perform RAG|


## S3
| Name  | Description  |
|---|---|
| chatbot-document-bucket-{accountId}  | stores all files for the knowledge base |
| chatbot-vector-bucket | stores vector for the document bucket |



## Knowledge Base
| Name  | Description  |
|---|---|
| chatbot-knowledge-base-{accountId} | The knowledge base |