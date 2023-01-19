# 
# Notion Lambda Automation
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



output "function_name" {
	description = "Lambda Function name."
	value = aws_lambda_function.main.function_name
}

output "arn" {
	description = "Lambda Function ARN."
	value = aws_lambda_function.main.arn
}

output "invoke_arn" {
	description = "Lambda Function invoke ARN."
	value = aws_lambda_function.main.invoke_arn
}