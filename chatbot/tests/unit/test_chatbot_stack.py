import aws_cdk as core
import aws_cdk.assertions as assertions

from stacks.chatbot_stack import ChatbotStack


# example tests. To run these tests, uncomment this file along with the example
# resource in chatbot/chatbot_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = ChatbotStack(app, "chatbot")
    template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
