# 
# Notion Lambda Automation
# 
# 
# Author: Marcelo Tellier Sartori Vaz <marcelotsvaz@gmail.com>



import logging
import os

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from notion_client import Client



def main( event, context ):
	logging.getLogger().setLevel( logging.INFO )
	
	
	# Get Notion client.
	notion = Client( auth = os.environ['notionToken'] )
	
	
	# Get database by name.
	databaseId = notion.search(
		query = 'TESTDB',
		filter = { 'property': 'object', 'value': 'database' }
	)['results'][0]['id']
	
	
	# Get pages due today.
	dayEnd = datetime.now( ZoneInfo( 'America/Sao_Paulo' ) ).replace( hour = 23, minute = 59, second = 59, microsecond = 0 )
	pages = notion.databases.query(
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
	for page in pages:
		pageName = ''.join( segment['plain_text'] for segment in page['properties']['Name']['title'] ) or '<untitled>'
		dueTime = datetime.fromisoformat( page['properties']['Due date']['date']['start'] )
		
		if datetime.now( ZoneInfo( 'America/Sao_Paulo' ) ) > dueTime:
			logging.info( f'Moving page "{pageName}" to Done.' )
			
			notion.pages.update(
				page_id = page['id'],
				properties = {
					'Status': {
						'select': { 'name': 'Done' },
					},
				}
			)
			
		elif page['properties']['Status']['select']['name'] != 'Today':
			logging.info( f'Moving page "{pageName}" to Today.' )
			
			notion.pages.update(
				page_id = page['id'],
				properties = {
					'Status': {
						'select': { 'name': 'Today' },
					},
				}
			)
	
	
	# Get done tasks without completed time set.
	pages = notion.databases.query(
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
	for page in pages:
		pageName = ''.join( segment['plain_text'] for segment in page['properties']['Name']['title'] ) or '<untitled>'
		logging.info( f'Setting completed time of page: {pageName}' )
		
		# Proper support for ISO 8601 is only available in Python 3.11, so we set the timezone manually.
		utcIsoLastEdited = page['last_edited_time'].removesuffix( 'Z' )
		lastEdited = datetime.fromisoformat( utcIsoLastEdited ).replace( tzinfo = timezone.utc ).astimezone( ZoneInfo( 'America/Sao_Paulo' ) )
		
		notion.pages.update(
			page_id = page['id'],
			properties = {
				'Completed time': {
					'date': {
						'start': lastEdited.isoformat(),
					},
				},
			}
		)