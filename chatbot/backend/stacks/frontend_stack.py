from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    CfnOutput,
    RemovalPolicy,
    Tags,
)
from constructs import Construct
from .environment import PROJECT_NAME
import subprocess
import os
import platform


class FrontendStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        Tags.of(self).add(key="PROJECT", value=PROJECT_NAME)

        api_url = self.node.try_get_context("api_url")

        # Correct path calculation
        frontend_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
        )

        # Create the .env.production file
        env_file_path = os.path.join(frontend_path, ".env.production")
        env_content = f"VITE_API_URL={api_url}"

        with open(env_file_path, "w") as f:
            f.write(env_content)

        print(f"Created .env.production at: {env_file_path}")
        print(f"Content: {env_content}")

        # Use the correct npm command for Windows
        npm_cmd = "npm.cmd" if platform.system() == "Windows" else "npm"

        try:
            # Build the app with shell=True for Windows
            print("Running npm install...")
            subprocess.run(
                [npm_cmd, "install"], cwd=frontend_path, check=True, shell=True
            )

            print("Running npm run build...")
            subprocess.run(
                [npm_cmd, "run", "build"], cwd=frontend_path, check=True, shell=True
            )

            print("Build completed successfully!")

        except subprocess.CalledProcessError as e:
            print(f"Build failed: {e}")
            raise Exception(f"Frontend build failed: {e}")

        # S3 bucket for hosting
        website_bucket = s3.Bucket(
            self,
            f"{PROJECT_NAME}-WebsiteBucket",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=True,
                block_public_policy=False,  # Allow public bucket policies
                ignore_public_acls=True,
                restrict_public_buckets=False,  # Allow public bucket access
            ),
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Deploy the built files
        s3deploy.BucketDeployment(
            self,
            f"{PROJECT_NAME}-DeployWebsite",
            sources=[s3deploy.Source.asset("../frontend/dist")],
            destination_bucket=website_bucket,
        )

        CfnOutput(
            self,
            "WebsiteUrl",
            value=website_bucket.bucket_website_url,
            description="Frontend URL",
        )
