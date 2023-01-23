# 
# Notion Helper
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



import logging
import os

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from notion_client import Client



def main( event, context ):
	'''
	Move tasks with `Due date` set to today to `Today` or `Done`.
	Set `Completed time` property on done tasks.
	'''
	
	del event, context	# Unused.
	logging.getLogger().setLevel( logging.INFO )
	
	
	# Variables.
	localTimezone = ZoneInfo( 'America/Sao_Paulo' )
	
	
	# Get Notion client.
	notion = Client( auth = os.environ['notionToken'] )
	
	
	# Get database by name.
	databaseId = notion.search(
		query = 'Tasks',
		filter = { 'property': 'object', 'value': 'database' }
	)['results'][0]['id']
	
	
	# Get today's tasks.
	dayEnd = datetime.now( localTimezone ).replace(
		hour = 23,
		minute = 59,
		second = 59,
		microsecond = 0,
	)
	tasks = notion.databases.query(
		database_id = databaseId,
		filter = {
			'and': [
				{
					'property': 'Due date',
					'date': { 'before': dayEnd.isoformat() }
				},
				{
					'property': 'Status',
					'select': { 'does_not_equal': 'Done' }
				},
			],
		},
	)['results']
	
	
	# Move due tasks.
	for task in tasks:
		taskName = ''.join(
			segment['plain_text'] for segment in task['properties']['Name']['title']
		) or '<untitled>'
		dueTime = datetime.fromisoformat( task['properties']['Due date']['date']['start'] )
		
		if datetime.now( localTimezone ) > dueTime:
			logging.info( f'Moving task "{taskName}" to Done.' )
			
			notion.pages.update(
				page_id = task['id'],
				properties = {
					'Status': {
						'select': { 'name': 'Done' },
					},
				}
			)
			
		elif task['properties']['Status']['select']['name'] != 'Today':
			logging.info( f'Moving task "{taskName}" to Today.' )
			
			notion.pages.update(
				page_id = task['id'],
				properties = {
					'Status': {
						'select': { 'name': 'Today' },
					},
				}
			)
	
	
	# Get done tasks without completed time set.
	tasks = notion.databases.query(
		database_id = databaseId,
		filter = {
			'and': [
				{
					'property': 'Status',
					'select': { 'equals': 'Done' }
				},
				{
					'property': 'Completed time',
					'date': { 'is_empty': True }
				},
			],
		},
	)['results']
	
	
	# Update completed time.
	for task in tasks:
		taskName = ''.join(
			segment['plain_text'] for segment in task['properties']['Name']['title']
		) or '<untitled>'
		logging.info( f'Setting completed time of task: {taskName}' )
		
		# Proper support for ISO 8601 is only available in Python 3.11, so we set the timezone manually.
		utcIsoLastEdited = task['last_edited_time'].removesuffix( 'Z' )
		lastEdited = datetime.fromisoformat( utcIsoLastEdited )
		lastEdited = lastEdited.replace( tzinfo = timezone.utc ).astimezone( localTimezone )
		
		notion.pages.update(
			page_id = task['id'],
			properties = {
				'Completed time': {
					'date': {
						'start': lastEdited.isoformat(),
					},
				},
			}
		)