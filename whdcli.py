#!/usr/bin/python

import requests
import os
import sys
import json
from xml.parsers.expat import ExpatError

try:
    import FoundationPlist
except ImportError as e:
    if os.uname()[0] == 'Darwin':
        print("Warning: Import of FoundationPlist failed: %s" % e)
        print("See README for information on this issue.")
    import plistlib

# this preference-reading code is shamelessly stolen from sheagcraig's python-jss
# https://github.com/sheagcraig/python-jss/blob/master/jss/jss.py#L76

class WHDPrefsMissingFileError(Exception):
	pass

class WHDPrefsMissingKeyError(Exception):
	pass
	
class WHDGetError(Exception):
	pass

class WHDPrefs(object):
	def __init__(self, preferences_file=None):
		if preferences_file is None:
			preferences_file = '~/Library/Preferences/com.github.nmcspadden.whd-cli.plist'
		preferences_file = os.path.expanduser(preferences_file)
		if os.path.exists(preferences_file):
			try:
				prefs = FoundationPlist.readPlist(preferences_file)
			except NameError:
				# Plist files are probably not binary on non-OS X machines, so
				# this should be safe.
				try:
					prefs = plistlib.readPlist(preferences_file)
				except ExpatError:
					raise WHDPrefsMissingFileError("This plist is malformed.  Please fix it and try again.")
			try:
				self.apikey = prefs['apikey']
				self.whd_url = prefs['whd_url'] 
			except KeyError:
				raise WHDPrefsMissingKeyError("Missing keys from plist.")
		else:
			raise WHDPrefsMissingFileError("Missing preference file!")

class WHD(object):
	def __init__(self, whd_prefs=None, url=None, apikey=None, verbose=True):
		if whd_prefs is not None:
			url = whd_prefs.whd_url
			apikey = whd_prefs.apikey
		
		self._url = '%s/helpdesk/WebObjects/Helpdesk.woa/' % url
		self.apikey = apikey
		self.verbose = verbose
		self.session = requests.Session()
		headers = {'content-type': 'application/json'}
		self.session.headers.update(headers)
	
	#stolen shamelessly from sheagcraig	
	def _error_handler(self, exception_cls, response):
		"""Generic error handler. Converts html responses to friendlier
		text.

		"""
		# Responses are sent as html. Split on the newlines and give us the
		# <p> text back.
		errorlines = response.text.encode('utf-8').split('\n')
		error = []
		for line in errorlines:
			e = re.search(r'<p.*>(.*)</p>', line)
			if e:
				error.append(e.group(1))

		error = '\n'.join(error)
		exception = exception_cls('JSS Error. Response Code: %s\tResponse" %s' %
								  (response.status_code, error))
		exception.status_code = response.status_code
		raise exception
		
	def getAssetList(self, limit=1500):
		url = '%s%s%s&apiKey=%s' % (self._url, 'ra/Assets?limit=', limit, self.apikey)
		response = self.session.get(url)
		
		if response.status_code == 200:
			if self.verbose:
				print("GET: Success")
		elif response.status_code >= 400:
			self._error_handler(WHDGetError, response)
			
		# results are in JSON
		whd_results = response.json()
		return whd_results
	
