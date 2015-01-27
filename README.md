WHD-CLI
===

This project is based on (and, to be honest, copied heavily from) Shea Craig's incredibly useful [Python-JSS](https://github.com/sheagcraig/python-jss) project.  That served as both the inspiration and functional template for the implementation of this tool.

This tool is a Python-based interface for [WebHelpDesk](http://www.webhelpdesk.com/) by way of its very thorough [REST API](http://www.solarwinds.com/documentation/webhelpdesk/docs/whd_api_12.2.0/web%20help%20desk%20api.html).

This is an ongoing work in progress, designed to accommodate the immediate functionality I need - primarily, what's been implemented is querying assets.

The primary use case for this script right now is with my Docker containers, both in [Puppetmaster-WHDCLI](https://osxdominion.wordpress.com/2015/01/26/using-puppet-with-webhelpdesk-to-sign-certs-in-yes-you-guessed-it-docker/) and as an [inventory tracker with Sal](https://osxdominion.wordpress.com/2015/01/22/how-to-setup-sal-sal-whd-and-jssimport-with-docker-2/).

It can certainly be used on its own, as an independent script, and it also exists as a separate [Docker container](https://registry.hub.docker.com/u/nmcspadden/whdcli/).

Install the Script:
----
This script exists only as a module and is not on PyPl, so you'll need to manually install it.

You'll need [Python-setuptools](http://pythonhosted.org//setuptools/) installed.

Download or clone the repo:  
`git clone https://github.com/nmcspadden/WHD-CLI.git`  
Then navigate inside and run setup.py:  
`python setup.py install`  

To Use This Script:
----

You need to populate the com.github.nmcspadden.whd-cli.plist file first.

1.  Generate a [WebHelpDesk API key](http://www.solarwinds.com/documentation/webhelpdesk/docs/whd_api_12.1.0/web%20help%20desk%20api.html#auth-tech-api-key) and copy and paste it into the value for the "apikey" key in the plist.
2.	Fill out the URL to your WHD instance (at its root), with port number.
3.  This file can be placed anywhere you can locate with Python.

Run the Python interpreter and import the module:  
`>>> import whdcli`  
You can instantiate the script in two ways:

1.  Load the preferences file by specifying the path to your plist:  
`>>> whd_prefs = whdcli.WHDPrefs("/Library/Preferences/com.github.nmcspadden.whd-cli.plist")`  
`>>> w = whdcli.WHD(whd_prefs, None, None)`  
2.	Alternatively, you can pass a URL and apikey directly into the function call:  
`>>> w = whdcli.WHD(None, url, apikey)`  

If you want to decrease verbosity in production, add a False to the end of the WHD() function call:  
`>>> w = whdcli.WHD(whd_prefs, None, None, False)` 

Querying Objects:
----
There are a few ways to search for asset inventory objects.  All of them return JSON results, from the API, and some of the functions provide a formatting option for better human readability.  

In these functions, the variable "nice" corresponds to whether you want a nice printed result that's more readable. Set "nice" to True if you want nice printing.

You can directly call these functions:  

*	`w.getAssetBySerial(serialNumber, nice)`  
	*	serialNumber should be a string.
*	`w.getAssetByMACAddress(MACaddress, nice)`  
	*	MACaddress should be a string.
*	`w.getAssetNumber(assetNumber)`  
	*	assetNumber refers to WebHelpDesk's internal asset numbering system. Only useful if you know ahead of time (or have web access to the system and are doing comparisons).
	
Or you can "search" for an item by [qualifier](http://www.solarwinds.com/documentation/webhelpdesk/docs/whd_api_12.2.0/web%20help%20desk%20api.html#common-parameters-qualifier):

*	`w.getDetailedAssetByAttribute(attribute, value, nice)`
	*	For example, `w.getDetailedAssetByAttribute('serialNumber',serial)` is identical to `w.getAssetBySerial(serial)`. 
	
Qualifiers can be any attribute built into WebHelpDesk (a good list is [here](http://www.solarwinds.com/documentation/webhelpdesk/docs/whd_api_12.2.0/web%20help%20desk%20api.html#assets-search)), or custom fields.

You can obtain a list of custom fields with this function:

*	`w.getAssetCustomFieldsFromAPI(limit=1500)`
	*	The API allows [customizing the limit on returned values](http://www.solarwinds.com/documentation/webhelpdesk/docs/whd_api_12.2.0/web%20help%20desk%20api.html#common-parameters-paging), which you can specify to a certain degree.  The upper limit is configured in WebHelpDesk.
	
At the moment, WHD-CLI has no support for making changes to assets - it's currenly read-only, although PUT/POST support is something I plan to implement someday.  Pull requests are welcome!