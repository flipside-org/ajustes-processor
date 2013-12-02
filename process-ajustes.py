#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Use this to prepare data on Ajustes Diretos (non-bid contracts) from the
# Portuguese government for import into Open Spending. The data is provided in
# a file with one JSON document per line and processed into a CSV.
# Source of the data: http://www.base.gov.pt

# Usage: $ python process-ajustes.py [file-name]

import csv
import json
import sys
import os
import fileinput
from datetime import datetime

# Check if the file-name is passed as an argument
if len(sys.argv) > 1:
	file_name = sys.argv[1]
	file_in = file_name + '.json'
	file_out = file_name + '.csv'
else:
    print 'Please provide the name of the file that should be processed. Eg. $ python process-ajustes.py [data_file]'
    exit (1)

# Check if there is a JSON with that name
if os.path.isfile(file_in) == False:
	print 'Oh my, something went wrong. Are you sure there is a file called \'' + file_in + '\'?'
	exit(1)

# Check if output csv already exists.
if os.path.isfile(file_out):
	print 'There is already a CSV file named ' + file_out + '.'
	exit(1)

with open(file_out, "w") as file:
	csv_file = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

	# Write the header
	csv_file.writerow(['signing_date', 'description', 'amount', 'execution_deadline', 'exection_place', 'publication_date', 'id', 'cpvs_id', 'cpvs_description', 'contract_types', 'object_description', 'contract_fundamentation', 'direct_award_fundamentation', 'contracted_id', 'contracted_nif', 'contracted_name', 'contracting_id', 'contracting_nif', 'contracting_name', 'observations', 'close_date', 'cause_deadline_change', 'total_price', 'cause_price_change'])
	
	# Loop over each of the contracts
	for line in fileinput.input(file_in):

		item = json.loads(line)

		# Clean up the currency field: 1) remove thousand seperator; 2) remove
		# the currency; and 3) substitute decimal mark ',' for '.'
		list_prices = ['initialContractualPrice', 'totalEffectivePrice']

		for price in list_prices:
			if item[price]:
				item[price] = item[price].encode('utf-8').translate(None, '. €').replace(',', '.')

		# Convert dates to proper format (eg. 2013-10-23)
		list_dates = ['publicationDate', 'signingDate', 'closeDate']

		for date in list_dates:
			if item[date]:
				item[date] = datetime.strptime(item[date], '%d-%m-%Y').date()

		# Split the CPV code from its description
		cpvs_id = item['cpvs'].split(',', 1)[0].strip()
		cpvs_description = item['cpvs'].split(',', 1)[1].strip().encode('utf-8')

		# Encode the texts
		list_longtexts = ['description', 'executionDeadline', 'observations', 'contractTypes', 'objectBriefDescription', 'contractFundamentationType', 'directAwardFundamentationType', 'causesDeadlineChange', 'causesPriceChange']

		for longtext in list_longtexts:
			if item[longtext]:
				item[longtext] = item[longtext].encode('utf-8')

		# Multiple locations are split with '<BR/>' substitute these for ' | '
		item['executionPlace'] = item['executionPlace'].encode('utf-8').replace('<BR/>', ' | ')

		# In some cases there are several contracting and contracted entities.
		# Since openspending doesn't support this, we combine these into a new
		# unique entity.
		# Process the contracted entities

		if len(item['contracted']) > 1:
			list_nif = []
			list_id = []
			list_name = []
			for contracted in item['contracted']:
				list_nif.append(contracted['nif'])
				list_id.append(str(contracted['id']))
				list_name.append(contracted['description'].encode('utf-8'))
			contracted_nif = ' | '.join(list_nif)
			contracted_id = ' | '.join(list_id)
			contracted_name = ' | '.join(list_name)
		else:
			contracted_nif = item['contracted'][0]['nif']
			contracted_id = item['contracted'][0]['id']
			contracted_name = item['contracted'][0]['description'].encode('utf-8')

		#Process the contracting entities
		
		if len(item['contracting']) > 1:
			list_nif = []
			list_id = []
			list_name = []
			for contracting in item['contracting']:
				list_nif.append(contracting['nif'])
				list_id.append(str(contracting['id']))
				list_name.append(contracting['description'].encode('utf-8'))
			contracting_nif = ' | '.join(list_nif)
			contracting_id = ' | '.join(list_id)
			contracting_name = ' | '.join(list_name)
		else:
			contracting_nif = item['contracting'][0]['nif']
			contracting_id = item['contracting'][0]['id']
			contracting_name = item['contracting'][0]['description'].encode('utf-8')

		# Write everything to the CSV file in the right order
		csv_file.writerow([item['signingDate'], item['description'], item['initialContractualPrice'], item['executionDeadline'], item['executionPlace'], item['publicationDate'], item['id'], cpvs_id, cpvs_description, item['contractTypes'], item['objectBriefDescription'], item['contractFundamentationType'], item['directAwardFundamentationType'], contracted_id, contracted_nif, contracted_name, contracting_id, contracting_nif, contracting_name, item['observations'], item['closeDate'], item['causesDeadlineChange'], item['totalEffectivePrice'], item['causesPriceChange']])

	print 'Data was written to ' + file_out + '.'