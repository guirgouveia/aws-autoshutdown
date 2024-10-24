# Function Deployment and Invocation Guide

## Requirements

### Set Up Python Environment

Make sure you have Python installed. You can set up a virtual environment for your project:

```shell
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install AWS CLI

Follow the instructions to install the AWS Command Line Interface (CLI) from the official AWS documentation.

## Overview

This guide will walk you through deploying and invoking serverless functions using Taskfile and AWS Lambda. This Lambda function is automatically deployed to AWS Lambda when you push to the main branch.

## Deploying the Function

To deploy the function, run:

```shell
serverless deploy
```

## Invoking the Function Locally

### To Shutdown ECS Services:

```shell
serverless invoke local --function shutdownECS
```

### To Turn On ECS Services:

```shell
serverless invoke local --function turnOnECS
```

## Configuration

### Environment Variables

Ensure you have the following environment variables set:

- `CLUSTERS_NAMES`: Comma-separated list of ECS cluster names.

### AWS Configuration

Make sure your AWS credentials are configured. You can use the AWS CLI to configure them:

```shell
aws configure
```

### Taskfile

The `Taskfile.yaml` contains the tasks for deploying and invoking the functions.

### Serverless Configuration

The `serverless.yml` file contains the configuration for the Serverless Framework.

### CloudFormation Resources

The `cloud-formation-resources.yml` file contains the IAM roles and policies required for the Lambda functions.

## Additional Information

For more details, refer to the official documentation of the tools and services used in this project:

- [Task](https://taskfile.dev/)
- [Python](https://www.python.org/doc/)
- [pip](https://pip.pypa.io/en/stable/)
- [AWS CLI](https://aws.amazon.com/cli/)
- [Serverless Framework](https://www.serverless.com/framework/docs/)