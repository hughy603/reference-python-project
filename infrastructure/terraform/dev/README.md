<!-- BEGIN_TF_DOCS -->

## Usage

Basic usage example:

```hcl
module "example" {
  source = "../../modules/example"

  # Required variables
  name        = "example-resource"
  environment = "dev"

  # Optional variables
  # tags       = { Team = "DevOps" }
}
```

## Requirements

| Name                                                                     | Version  |
| ------------------------------------------------------------------------ | -------- |
| <a name="requirement_terraform"></a> [terraform](#requirement_terraform) | >= 1.0.0 |
| <a name="requirement_aws"></a> [aws](#requirement_aws)                   | ~> 5.0   |

## Providers

| Name                                             | Version |
| ------------------------------------------------ | ------- |
| <a name="provider_aws"></a> [aws](#provider_aws) | ~> 5.0  |

## Modules

No modules.

## Resources

| Name                                                                                                                                                            | Type     |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| [aws_api_gateway_deployment.deployment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_deployment)                     | resource |
| [aws_api_gateway_integration.integration](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_integration)                  | resource |
| [aws_api_gateway_method.method](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_method)                                 | resource |
| [aws_api_gateway_resource.resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_resource)                           | resource |
| [aws_api_gateway_rest_api.api](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_rest_api)                                | resource |
| [aws_cloudwatch_log_group.lambda_logs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_log_group)                        | resource |
| [aws_iam_policy.lambda_s3_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_policy)                                       | resource |
| [aws_iam_role.lambda_execution_role](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role)                                      | resource |
| [aws_iam_role_policy_attachment.lambda_basic_execution](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_iam_role_policy_attachment.lambda_s3_access](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment)       | resource |
| [aws_lambda_function.data_engineering](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function)                             | resource |
| [aws_lambda_permission.api_gateway](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission)                              | resource |

## Inputs

| Name                                                                                                | Description                              | Type     | Default       | Required |
| --------------------------------------------------------------------------------------------------- | ---------------------------------------- | -------- | ------------- | :------: |
| <a name="input_aws_region"></a> [aws_region](#input_aws_region)                                     | AWS region to deploy resources           | `string` | `"us-east-1"` |    no    |
| <a name="input_environment"></a> [environment](#input_environment)                                  | Deployment environment (dev, test, prod) | `string` | `"dev"`       |    no    |
| <a name="input_lambda_package_bucket"></a> [lambda_package_bucket](#input_lambda_package_bucket)    | S3 bucket containing the Lambda package  | `string` | n/a           |   yes    |
| <a name="input_lambda_package_version"></a> [lambda_package_version](#input_lambda_package_version) | Version of the Lambda package to deploy  | `string` | n/a           |   yes    |

## Outputs

| Name                                                                                            | Description                 |
| ----------------------------------------------------------------------------------------------- | --------------------------- |
| <a name="output_api_endpoint"></a> [api_endpoint](#output_api_endpoint)                         | API Gateway endpoint URL    |
| <a name="output_lambda_function_arn"></a> [lambda_function_arn](#output_lambda_function_arn)    | ARN of the Lambda function  |
| <a name="output_lambda_function_name"></a> [lambda_function_name](#output_lambda_function_name) | Name of the Lambda function |

## Examples

For more detailed examples, see the [examples](../../examples) directory.

<!-- END_TF_DOCS -->
