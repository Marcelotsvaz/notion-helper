# 
# Notion Helper
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



terraform {
	required_providers {
		aws = {
			source = "hashicorp/aws"
			version = "5.23.1"
		}
	}
	
	required_version = ">= 1.3.6"
}