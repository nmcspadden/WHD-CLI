#!/usr/bin/python

import requests
import os
import sys
import json
import re
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
		self.customFieldsDict = dict()
		for customField in self.getAssetCustomFieldsFromAPI():
			self.customFieldsDict[customField['id']] = customField['label']
			#now we can access the label for a given attribute 
	
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
		exception = exception_cls('WHD Error. Response Code: %s\tResponse" %s' % (response.status_code, error))
		exception.status_code = response.status_code
		raise exception

	def get(self, url):
		"""Generic URL retrieval"""
		url = '%s%s&apiKey=%s' % (self._url, url, self.apikey)
		if self.verbose:
			print "get URL: %s" % url
		response = self.session.get(url)
		if response.status_code == 200:
			if self.verbose:
				print("GET: Success")
		elif response.status_code >= 400:
			self._error_handler(WHDGetError, response)			
		return response

	def getItemQualifier(self, item, qualifier):
		"""Generic qualifier - use as a template for other specifics"""
		url = 'ra/%s?qualifier=(%s)' % (str(item), str(qualifier))
		if self.verbose:
			print "getItemQualifier URL: %s" % url
		response = self.get(url)
		return response.json()

	def getAssetList(self, limit=1500):
		url = 'ra/Assets?limit=%s' % str(limit)
		response = self.get(url)
		return response.json()

	def getAssetNumber(self, assetNumber):
		url = 'ra/Assets?assetNumber=%s' % str(assetNumber)
		response = self.get(url)
		return response.json()
		
	def getAsset(self, assetNumber):
		url = '%sra/Assets/%s?apiKey=%s' % (self._url, str(assetNumber), self.apikey)
		if self.verbose:
			print "getAsset URL: %s" % url
		response = self.session.get(url)
		if response.status_code == 200:
			if self.verbose:
				print("GET: Success")
		elif response.status_code >= 400:
			self._error_handler(WHDGetError, response)
		return response.json()
		
	def getAssetStatusList(self, limit=1500):
		url = 'ra/AssetStatuses?limit=%s' % str(limit)
		response = self.get(url)
		return response.json()

	def getAssetStatus(self, assetStatusNumber):
		url = 'ra/AssetStatuses/%s' % str(assetStatusNumber)
		response = self.get(url)
		return response.json()

	def getDetailedAssetByAttribute(self, attribute, value, nice=False):
		qualifier = '%s %%3D \'%s\'' % (attribute, value)
		result = self.getItemQualifier('Assets', qualifier)
		if not result:
			if self.verbose:
				print "No matching results."
			return False
		response = self.getAsset(result[0]['id'])
		if nice:
			return json.dumps(response, indent=4)
		else:
			#this returns as a Python dict
			return response
			
	def getAssetBySerial(self, serialNumber, nice=False):
		return self.getDetailedAssetByAttribute('serialNumber', serialNumber, nice)
		
	def getAssetByMACAddress(self, MACaddress, nice=False):
		return self.getDetailedAssetByAttribute('macAddress', MACaddress, nice)
		
	def getAssetCustomFieldsFromAPI(self, limit=1500):
		url = 'ra/CustomFieldDefinitions/Asset?limit=%s' % str(limit)
		response = self.get(url)
		#the expected result here is that you get a Python list of dicts
		return response.json()
		
	def retrieveCustomFieldNamesFromID(self, id):
		customFieldLabels = list()
		
		

class WHDAsset(object):
	def __init__(self, whd, json):
		#Base class for WHD Assets
		if not isinstance(whd, WHD):
			raise TypeError("Argument whd must be an instance of WHD.")
		self.whd = whd
		#for now, assume json is a dict
		#assign all the variables to locals
		self.id = json['id']
		self.type = json['type']
		self.assetNumber = json['assetNumber']
		self.macAddress = json['macAddress']
		self.networkName = json['networkName']
		self.warrantyExpirationDate = json['warrantyExpirationDate']
		self.billingRate = json['billingRate']
		self.purchaseDate = json['purchaseDate']
		self.isReservable = json['isReservable']
		self.isSynchronizationDisabled = json['isSynchronizationDisabled']
		self.warrantyType = json['warrantyType']
		self.assetstatus = json['assetstatus']
		self.isDeleted = json['isDeleted']
		self.isNotesVisibleToClients = json=['isNotesVisibleToClients']
		self.version = json['version']
		self.location = json['location']
		self.type = json['type']
		self.networkName = json['networkName']
		self.model = json['model']
		self.networkAddress = json['networkAddress']
		self.contractExpiration = json['contractExpiration']
		self.notes = json['notes']
		self.clients = json['clients']
		self.leaseExpirationDate = json['leaseExpirationDate']
		#deal with custom fields in a special way
		#custom fields are a Python dictionary
		customFieldsList = json['assetCustomFields']
		
class WHDAssetCustomField(object):
	def __init__(self, customField):
		#Class for custom fields specifically for assets
		if not isinstance(customField, dict):
			raise TypeError("Argument customField must be a Python dict.")
		self.customField = customField
		