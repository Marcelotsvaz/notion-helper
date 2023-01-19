# 
# Notion Lambda Automation
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



# 
# Notion Lambda Automation
#-------------------------------------------------------------------------------
module "notion" {
	source = "./module/lambda"
	
	name = local.name
	identifier = local.identifier
	
	source_dir = "src"
	handler = "main.main"
	environment = { notionToken = var.notion_token }
	layers = [ aws_lambda_layer_version.dependencies.arn ]
	
	# policies = [ data.aws_iam_policy_document.webhook_handler ]
}


resource "aws_lambda_layer_version" "dependencies" {
	layer_name = "${local.identifier}-pythonPackages"
	filename = data.archive_file.dependencies.output_path
}


data "archive_file" "dependencies" {
	type = "zip"
	source_dir = "deployment/env/lib/python3.10/"
	output_path = "/tmp/terraform/module.zip"
}


# data "aws_iam_policy_document" "webhook_handler" {
# 	statement {
# 		sid = "invokeJobMatcherFunction"
		
# 		actions = [ "lambda:InvokeFunction" ]
		
# 		resources = [ module.job_matcher.arn ]
# 	}
# }


# resource "aws_lambda_permission" "webhook_handler" {
# 	function_name = module.webhook_handler.function_name
# 	statement_id = "lambdaInvokeFunction"
# 	principal = "apigateway.amazonaws.com"
# 	action = "lambda:InvokeFunction"
# 	source_arn = "${aws_apigatewayv2_stage.main.execution_arn}/${replace( aws_apigatewayv2_route.webhook_handler.route_key, " ", "")}"
# }