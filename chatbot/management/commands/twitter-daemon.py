from django.core.management.base import BaseCommand, CommandError
from chatbot.models import cbot 
import chatbot.script.process_manager as pm
import time
import datetime
## This is a custom django command which can be accessed through the manage.py - 
## I've added this in order to link a cron task which should run on the server every so often
## This can be very frequently, or alternatively if there are load/performance issues it can be dropped

class Command(BaseCommand):
	help = 'Checks all active chatbots in database and runs if True'

	## the handle is the command executer
	def handle(self, *args, **options):
		try:
			for n in range(3): ## Because we use cron and the minimum limit is 1 minute, we'll just do it twice after waiting 25 seconds
				for n in cbot.objects.all():
					if n.enabled == True:       
						pm.deploy_cbot_process(n.id)
				time.sleep(15)
		except Exception, e:
			cron_task_log = open('/home/teachertest/public_html/cgi-bin/cronlog.txt', 'a')
			cron_task_log.write("\n" + str(e))