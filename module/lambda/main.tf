# 
# Notion Helper
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



# 
# Lambda Function
#-------------------------------------------------------------------------------
resource aws_lambda_function main {
	function_name = local.lambda_function_name
	role = aws_iam_role.main.arn
	
	runtime = "python3.9"
	filename = data.archive_file.main.output_path
	source_code_hash = data.archive_file.main.output_base64sha256
	handler = var.handler
	timeout = var.timeout
	layers = var.layers
	
	environment {
		variables = merge( var.environment, {
			PYTHONPATH = "/opt/site-packages"
			terraformParameters = jsonencode( var.parameters )
		} )
	}
	
	# Make sure the log group is created before the function because we removed the implicit dependency.
	depends_on = [ aws_cloudwatch_log_group.main ]
	
	tags = {
		Name = "${var.name} Lambda"
	}
}


data archive_file main {
	type = "zip"
	source_dir = var.source_dir
	output_path = "/tmp/terraform/${var.identifier}/module.zip"
}



# 
# CloudWatch
#-------------------------------------------------------------------------------
resource aws_cloudwatch_log_group main {
	name = "/aws/lambda/${local.lambda_function_name}"
	
	tags = {
		Name = "${var.name} Lambda Log Group"
	}
}



# 
# Lambda IAM Role
#-------------------------------------------------------------------------------
resource aws_iam_role main {
	name = var.identifier
	assume_role_policy = data.aws_iam_policy_document.assume_role.json
	managed_policy_arns = []
	
	inline_policy {
		name = "${var.identifier}-logs"
		policy = data.aws_iam_policy_document.logs.json
	}
	
	dynamic "inline_policy" {
		for_each = var.policies
		
		content {
			name = "${var.identifier}-policy"
			policy = inline_policy.value.json
		}
	}
	
	tags = {
		Name: "${var.name} Lambda Role"
	}
}


data aws_iam_policy_document assume_role {
	statement {
		sid = "lambdaAssumeRole"
		
		principals {
			type = "Service"
			identifiers = [ "lambda.amazonaws.com" ]
		}
		
		actions = [ "sts:AssumeRole" ]
	}
}


data aws_iam_policy_document logs {
	statement {
		sid = "putCloudwatchLogs"
		
		actions = [
			"logs:CreateLogStream",
			"logs:PutLogEvents",
		]
		
		resources = [ "${aws_cloudwatch_log_group.main.arn}:*" ]
	}
}