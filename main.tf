# 
# Notion Helper
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



# 
# Notion Helper
#-------------------------------------------------------------------------------
module notion_helper {
	source = "gitlab.com/marcelotsvaz/lambda/aws"
	version = "~> 0.2.0"
	
	name = local.name
	identifier = local.identifier
	
	source_dir = "src"
	handler = "notionHelper.main"
	environment = { notionToken = var.notion_token }
	layers = [ aws_lambda_layer_version.python_packages.arn ]
}


resource aws_lambda_layer_version python_packages {
	layer_name = "${local.identifier}-pythonPackages"
	filename = data.archive_file.python_packages.output_path
}


data archive_file python_packages {
	type = "zip"
	source_dir = "deployment/env/lib/python3.10/"
	output_path = "/tmp/terraform/python_packages.zip"
}


resource aws_lambda_permission main {
	function_name = module.notion_helper.function_name
	statement_id = "lambdaInvokeFunction"
	principal = "events.amazonaws.com"
	action = "lambda:InvokeFunction"
	source_arn = aws_cloudwatch_event_rule.main.arn
}



# 
# EventBridge
#-------------------------------------------------------------------------------
resource aws_cloudwatch_event_rule main {
	name = "${local.identifier}-schedule"
	schedule_expression = "rate(1 minute)"
	
	tags = {
		Name = "${local.name} Event Rule"
	}
}


resource aws_cloudwatch_event_target main {
	rule = aws_cloudwatch_event_rule.main.name
	arn = module.notion_helper.arn
}