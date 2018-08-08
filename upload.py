#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script for batch uploading photos to tumblr, and applying a set of tags to all photos.

usage: upload.py [-h] [-t TAGS] directory
ex:	   upload.py -t "dc,2016,35mm,canon ae-1" ~/photos/color-dc/

- Uploads all JPG files in the specified directory.
- Requires pytumblr client https://github.com/tumblr/pytumblr
- Requires json credential file at ~/.tumblr with fields:
	'consumer_key', 'consumer_secret', 'oauth_token', 'oauth_token_secret'
"""

import argparse
import glob
import os
import pytumblr
import sys
import yaml

from os import listdir
from os.path import join


BLOG_NAME = 'internetgig'

def upload_files(client, files, tags):
	for f in files:
		print 'Uploading %s' % f
		client.create_photo(
			blogname=BLOG_NAME,
			state='published',
			tags=tags,
			data=f,
			format='html')

def query_confirm():
	valid_responses = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
	while True:
		sys.stdout.write("Continue? [y/N] ")
		choice = raw_input().lower()
		if choice == '':
			return False
		elif choice in valid_responses:
			return valid_responses[choice]
		else:
			sys.stdout.write("Please respond with 'y' or 'n'\n")

if __name__ == '__main__':
	# validate args
	parser = argparse.ArgumentParser(description='Upload photos to tumblr')
	parser.add_argument('directory', help='directory')
	parser.add_argument('-t', '--tags', help='comma-separated tags string')
	args = parser.parse_args()
	if not os.path.exists(args.directory):
		print 'directory does not exist'
		sys.exit(0)

	# read auth tokens
	yaml_path = os.path.expanduser('~') + '/.tumblr'
	if not os.path.exists(yaml_path):
		print 'credential file ~/.tumblr does not exist'
		sys.exit(0)

	yaml_file = open(yaml_path, "r")
	tokens = yaml.safe_load(yaml_file)
	yaml_file.close()
	if not all (k in tokens for k in (
		'consumer_key', 'consumer_secret', 'oauth_token', 'oauth_token_secret')
	):
		print 'credential file ~/.tumblr has incorrect format'
		sys.exit(0)
	
	# parse tags and list JPG files
	jpg_files = [os.path.join(args.directory, f) for f in listdir(args.directory) if f.lower().endswith('.jpg')]
	tags = [] if args.tags is None else args.tags.split(',')
	
	if len(jpg_files) < 1:
		print 'no jpg files found in directory'
		sys.exit(0)

	# confirm upload
	print '=====files=====\n%s\n' % '\n'.join(jpg_files)
	print '=====tags=====\n%s\n' % '\n'.join(tags)
	if not query_confirm():
		sys.exit(0)

	# create pytumblr client
	client = pytumblr.TumblrRestClient(
		tokens['consumer_key'],
		tokens['consumer_secret'],
		tokens['oauth_token'],
		tokens['oauth_token_secret']
	)

	# upload files
	upload_files(client, jpg_files, tags)

	print '\nall done! https://%s.tumblr.com' % BLOG_NAME
