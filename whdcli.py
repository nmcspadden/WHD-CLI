#!/usr/bin/python

import requests
import plistlib
import os

preferences_file = '~/Library/Preferences/com.github.nmcspadden.whd-cli.plist'
preferences_file = os.path.expanduser(preferences_file)