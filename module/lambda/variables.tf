# 
# Notion Helper
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



# 
# Name
#-------------------------------------------------------------------------------
variable name {
	description = "Name of the function."
	type = string
}

variable identifier {
	description = "Unique identifier used in resources that need an unique name."
	type = string
}


# 
# Code
#-------------------------------------------------------------------------------
variable source_dir {
	description = "Path of Python modules."
	type = string
}

variable handler {
	description = "Lambda function entrypoint."
	type = string
}

variable timeout {
	description = "Lambda function timeout."
	type = number
	default = 30
}

variable parameters {
	description = "Parameters automatically injected into module."
	type = any
	default = {}
}

variable environment {
	description = "Environment variables."
	type = map( string )
	default = {}
}

variable layers {
	description = "Set of Lambda layer ARNs."
	type = set( string )
	default = []
}


# 
# Permissions
#-------------------------------------------------------------------------------
variable policies {
	description = "Set of policies for the Lambda Function IAM role."
	type = set( object( { json = string } ) )
	default = []
}



# 
# Locals
#-------------------------------------------------------------------------------
locals {
	lambda_function_name = var.identifier	# Avoid cyclic dependency.
}