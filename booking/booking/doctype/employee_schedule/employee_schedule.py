# -*- coding: utf-8 -*-
# Copyright (c) 2018, August Infotech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import os
from frappe.utils import flt
# from ics import Calendar, Event

# import smtplib 
# from email.mime.multipart import MIMEMultipart 
# from email.mime.text import MIMEText 
# from email.mime.base import MIMEBase 
# from email import encoders 
# from frappe.desk.form.load import get_attachments
# from frappe.core.doctype.communication.email import make

class EmployeeSchedule(Document):
	def autoname(self):
		self.name = self.schedule_name

	def validate(self):
		match_found = 0
		for i in self.time_slots:
			is_matched = 0
			is_matched = self.compare_time(self.lunch_start_time, i.to_time)
			if is_matched:
				i.is_lunch_time = 1
			if not match_found:
				match_found = is_matched
		if not match_found:
			frappe.throw("There is no To Time matched with Lunch Start Time.")

	def compare_time(self,time1, time2):
		(h1, m1, s1) = str(time1).split(':')
		(h2, m2, s2) = str(time2).split(':')
		if int(h1) == int(h2) and int(m1) == int(m2) and int(s1) == int(s2):
			return 1
		else:
			return 0