# 
# Notion Helper
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



variable notion_token {
	description = "Notion API Token."
	type = string
	sensitive = true
}



locals {
	name = "Notion Helper"
	identifier = "notionHelper"
	
	default_tags = {
		Project = local.name
	}
}