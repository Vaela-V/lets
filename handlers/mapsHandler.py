import sys
import traceback

import tornado.gen
import tornado.web
from raven.contrib.tornado import SentryMixin

from common.log import logUtils as log
from common.web import requestsManager
from constants import exceptions
from helpers import osuapiHelper
from objects import glob

MODULE_NAME = "maps"
class handler(SentryMixin, requestsManager.asyncRequestHandler):
	@tornado.web.asynchronous
	@tornado.gen.engine
	def asyncGet(self, fileName = None):
		try:
			# Check arguments
			if fileName == None:
				raise exceptions.invalidArgumentsException(MODULE_NAME)
			if fileName == "":
				raise exceptions.invalidArgumentsException(MODULE_NAME)

			fileNameShort = fileName[:32]+"..." if len(fileName) > 32 else fileName[:-4]
			log.info("Requested .osu file {}".format(fileNameShort))

			# Get .osu file from osu! server
			fileContent = osuapiHelper.getOsuFileFromName(fileName)
			if fileContent == None:
				# TODO: Sentry capture message here
				raise exceptions.osuApiFailException(MODULE_NAME)
			self.write(fileContent)
		except exceptions.invalidArgumentsException:
			self.set_status(500)
		except exceptions.osuApiFailException:
			self.set_status(500)
		except:
			log.error("Unknown error in {}!\n```{}\n{}```".format(MODULE_NAME, sys.exc_info(), traceback.format_exc()))
			if glob.sentry:
				yield tornado.gen.Task(self.captureException, exc_info=True)
		#finally:
		#	self.finish()
