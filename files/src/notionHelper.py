# 
# Notion Helper
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



import logging
import os

from typing import Any
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from notion_client import Client



# Global variables.
localTimezone = ZoneInfo( 'America/Sao_Paulo' )



def main( event: dict[str, Any], context: Any ) -> None:
	'''
	Move tasks with `Due date` set to today to `Today` or `Done`.
	Set `Completed time` property on done tasks.
	'''
	
	del event, context	# Unused.
	logging.getLogger().setLevel( logging.INFO )
	
	
	# Get Notion client.
	notion = Client( auth = os.environ['notionToken'], timeout_ms = 10_000 )
	
	
	# Get database by name.
	databaseId: str = notion.search(	# pyright: ignore [reportGeneralTypeIssues]
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
	tasks: list[dict[str, Any]] = notion.databases.query(	# pyright: ignore [reportGeneralTypeIssues]
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
		dueTime = parseDatetime( task['properties']['Due date']['date']['start'] )
		
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
	tasks: list[dict[str, Any]] = notion.databases.query(	# pyright: ignore [reportGeneralTypeIssues]
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
		lastEdited = parseDatetime( task['last_edited_time'] )
		logging.info( f'Setting completed time of task: {taskName}' )
		
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



def parseDatetime( isoDate: str ) -> datetime:
	'''
	Parse a date in ISO 8601 format to a datetime object.
	'''
	
	date = datetime.fromisoformat( isoDate.removesuffix( 'Z' ) )
	
	if isoDate.endswith( 'Z' ):
		# Proper support for ISO 8601 is only available in Python 3.11, so we set the timezone
		# manually in this case.
		date = date.replace( tzinfo = timezone.utc ).astimezone( localTimezone )
	
	if date.tzinfo is None:
		# Notion dates without time are offset-naive, so consider them to be in local time.
		date = date.replace( tzinfo = localTimezone )
	
	return date