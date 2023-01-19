# 
# Notion Lambda Automation
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



# 
# Notion Lambda Automation
#-------------------------------------------------------------------------------
module "notion_lambda_automation" {
	source = "./module/lambda"
	
	name = local.name
	identifier = local.identifier
	
	source_dir = "src"
	handler = "main.main"
	environment = { notionToken = var.notion_token }
	layers = [ aws_lambda_layer_version.dependencies.arn ]
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


resource "aws_lambda_permission" "main" {
	function_name = module.notion_lambda_automation.function_name
	statement_id = "lambdaInvokeFunction"
	principal = "events.amazonaws.com"
	action = "lambda:InvokeFunction"
	source_arn = aws_cloudwatch_event_rule.main.arn
}



# 
# EventBridge.
#-------------------------------------------------------------------------------
resource "aws_cloudwatch_event_rule" "main" {
	name = "${local.identifier}-eventRule"
	schedule_expression = "rate(1 minute)"
	
	tags = {
		Name = "${local.name} Event Rule"
	}
}


resource "aws_cloudwatch_event_target" "main" {
	rule = aws_cloudwatch_event_rule.main.name
	arn = module.notion_lambda_automation.arn
}