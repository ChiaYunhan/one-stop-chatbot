# Resources

## API

| API | Lambda |
| ----| ---- |
| GetKnowledgeBase| AdminGetKnowledgeBase |
| CreateUpdateKnowledgeBase| AdminCreateUpdateKnowledgeBase |
| DeleteKnowledgeBase | AdminDeleteKnowledgeBase |
| GetUserChat | AdminGetUserChat |
| DeleteUserChat | AdminDeleteUserChat |


## DynamoDB

| DynamoDB  | Description  |
|---|---|
| KnowledgeBase  | dynamodb to store all created knowledge bases  |
| UserChat | dynamodb to store all user chats and their history |


### KnowledgeBase
| Column  | Type | Description |
|---|---| --- |
| knowledgeBaseId  | string  | primary key|
| createdAt  | string  | |
| updatedAt  | string  | |
| s3BucketFolder  | string  | s3 folder prefix containing all documents stored in the knowledge base|

### UserChat
| Column  | Type | Description |
|---|---| --- |
| userChatId  | string  | primary key|
| createdAt  | string  | |
| updatedAt  | string  | |
| chat | map | complete chat history of the conversation. Sample: {'user': '...', 'system': '...', ...}|



## S3
| s3  | Description  |
|---|---|
| documentBucket  | stores all files for the respective knowledge bases, separatedd by folder prefix  |


## Backend Lambda
| Lambda  | Reason  |
|---|---|
| SendUserQuery | This lambda will be triggered when a UserChat dynamodb record is created or updated and if the last input key in "chat" column is a "user" entry. This lambda will generate embedding from user input and query from the corresponding knowledge base.|


