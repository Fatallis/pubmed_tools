#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, os, re, uuid, subprocess
from bs4 import BeautifulSoup


def run_parallel(commands_file, remove=True):
	command=['parallel', '-k', '-a', commands_file]
	p=subprocess.Popen(command,stdout=subprocess.PIPE)
	output = p.stdout.read()
	if remove:
		os.remove(commands_file)

	return output


def search_pubmed(query):
	query=' '.join(query)
	search_commands='.'+uuid.uuid4().hex+'.txt'
	with open(search_commands,'w') as commands:
		commands.write('esearch -db pubmed -query "'+query+'" -sort "Pub Date" | efetch -format abstract -mode xml\n')

	xml=run_parallel(search_commands)

	return xml


def parse_paper(xml_paper):
	try:
		pmid=xml_paper.find('pmid').get_text().encode('utf-8')
	except AttributeError:
		pmid=''

	try:
		title=xml_paper.find('title').get_text().encode('utf-8')
	except AttributeError:
		title=''

	try:
		year=xml_paper.find('pubdate').find('year').get_text().encode('utf-8')
	except AttributeError:
		year=''

	try:
		lastname=xml_paper.find('lastname').get_text().encode('utf-8')
	except AttributeError:
		lastname=''

	try:
		articletitle=xml_paper.find('articletitle').get_text().encode('utf-8')
	except AttributeError:
		articletitle=''

	try:
		abstract=xml_paper.find('abstracttext').get_text().encode('utf-8')
	except AttributeError:
		abstract=''

	return [pmid,title,year,lastname,articletitle,abstract]


def get_abstracts(xml):
	soup = BeautifulSoup(xml, 'lxml')
	papers = soup.find_all("pubmedarticle")
	for p in papers:
		pmid,title,year,lastname,articletitle,abstract=parse_paper(p)
		
		filename=year+'_'+lastname+'_'+pmid+'.txt'
		with open(filename,'w') as txt:
			txt.write('# '+lastname+' '+year+'\n\n'+title+'\n\n## '+articletitle+'\n\n\n'+abstract+'\n')


query=sys.argv[1:]

xml=search_pubmed(query)
get_abstracts(xml)

