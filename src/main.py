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
	database = notion.search(
		query = 'TESTDB',
		filter = { 'property': 'object', 'value': 'database' }
	)['results'][0]
	
	
	# Get pages to update.
	databaseId = database['id']
	pages = notion.databases.query(
		database_id = databaseId,
		filter = {
			'and': [
				{
					'property': 'Status',
					'select': { 'equals': 'Done' }
				},
				{
					'property': 'Completed Time',
					'date': { 'is_empty': True }
				},
			],
		},
	)['results']
	
	
	# Update pages.
	for page in pages:
		pageName = ''.join( segment['plain_text'] for segment in page['properties']['Name']['title'] ) or '<untitled>'
		logging.info( f'Updating page: {pageName}' )
		
		# Proper support for ISO 8601 is only available in Python 3.11, so we set the timezone manually.
		utcIsoLastEdited = page['last_edited_time'].removesuffix( 'Z' )
		lastEdited = datetime.fromisoformat( utcIsoLastEdited ).replace( tzinfo = timezone.utc ).astimezone( ZoneInfo( 'America/Sao_Paulo' ) )
		
		notion.pages.update(
			page_id = page['id'],
			properties = {
				'Completed Time': {
					'date': {
						'start': lastEdited.isoformat(),
					},
				},
			}
		)