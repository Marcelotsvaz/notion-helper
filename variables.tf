# 
# Notion Lambda Automation
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



variable notion_token {
	description = "Notion API Token"
	type = string
	sensitive = true
}



locals {
	name = "Notion Lambda Automation"
	identifier = "notionLambdaAutomation"
	
	default_tags = {
		Project = local.name
	}
}