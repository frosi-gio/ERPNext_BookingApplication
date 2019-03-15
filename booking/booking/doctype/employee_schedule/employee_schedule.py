# -*- coding: utf-8 -*-
# Copyright (c) 2018, August Infotech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
import os
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
		pass
		# auto_email_report = frappe.get_doc('Auto Email Report', 'Stock Balance')
		# frappe.throw(str(auto_email_report.enabled))
		# frappe.msgprint(str(auto_email_report.filters))
		# auto_email_report.filters = {"from_date":"2019-02-14","to_date":"2019-03-14","show_variant_attributes":0}
		# filter_dict = str(auto_email_report.filters)
		# frappe.throw(str(auto_email_report.filters))
		# if type(filter_dict) is str:
		# 	frappe.throw("Yes")
		# else:
		# 	frappe.throw("No")
		# auto_email_report.filters["from_date"] = "2019-02-14"
		# auto_email_report.filters["to_date"] = "2019-02-14"
		# frappe.throw(auto_email_report.filters)
		# c = Calendar()
		# e = Event()
		# e.name = "[Unlimited Tomorrow]"
		# e.begin = '20190315 13:30:00'
		# e.end = '20190315 14:15:00'
		# e.location = 'Balzan'
		# e.description = "Hair Cut By Harsh"
		# c.events.add(e)

		# directory_path = frappe.get_site_path('public', 'files')
		# filepath = os.path.join(str(directory_path), 'unlimited_tomorrow_1.ics')

		# frappe.throw(str(c))
		# with open(filepath, 'w') as f:
		# 	f.writelines(c)

		# file_size = os.path.getsize(file_path)

		# frappe.throw(str(filepath))

		# file = frappe.get_doc({"doctype":"File", "file_name":"unlimited_tomorrow_1.ics","file_url":"/files/unlimited_tomorrow_1.ics","file_size":str(file_size), "attached_to_doctype":"Employee Schedule", "attached_to_name":"Nishith Schedule"})
		# file.insert()
		# file.save()

		# atch = get_attachments('Employee Schedule', 'Nishith Schedule')

		# frappe.throw(str(atch[0]['name']))

		# my_attachments = [frappe.attach_print('Item', 'beard oil', file_name='invite_(1).ics')]

		# frappe.throw(str(atch[0]['name']))

		# make(
		# recipients='nishith.kansara@augustinfotechteam.com',
		# subject="[Unlimited Tomorrow]",
		# content="Dear {}, Your appointment with Antonio Barber is approved.".format('Nishith'),
		# attachments = [atch[0]['name']],
		# send_email=True
		# )

		# frappe.delete_doc("File",str(atch[0]['name']))

		# frappe.sendmail(
		# recipients='nishith.kansara@augustinfotechteam.com',
		# subject="[Unlimited Tomorrow]",
		# message="Dear {}, Your appointment with Antonio Barber is approved.".format('Nishith'),
		# attachments = [atch[0]['name']],
		# now=True
		# )

		# fromaddr = "application.qa501@gmail.com"
		# toaddr = "raj.tailor@augustinfotechteam.com"
		   
		# # instance of MIMEMultipart 
		# msg = MIMEMultipart() 
		  
		# # storing the senders email address   
		# msg['From'] = fromaddr 
		  
		# # storing the receivers email address  
		# msg['To'] = toaddr 
		  
		# # storing the subject  
		# msg['Subject'] = "[Unlimited Tomorrow]"
		  
		# # string to store the body of the mail 
		# body = "Dear {}, Your appointment with Antonio Barber is approved.".format('Nishith')
		  
		# # attach the body with the msg instance 
		# msg.attach(MIMEText(body, 'plain')) 
		  
		# # open the file to be sent  
		# # filename = "File_name_with_extension"
		# attachment = open(filepath, "rb")
		  
		# # instance of MIMEBase and named as p 
		# p = MIMEBase('application', 'octet-stream') 
		  
		# # To change the payload into encoded form 
		# p.set_payload((attachment).read()) 
		  
		# # encode into base64 
		# encoders.encode_base64(p) 
		   
		# p.add_header('Content-Disposition', "attachment; filename= %s" % 'unlimited_tomorrow.ics') 
		  
		# # attach the instance 'p' to instance 'msg' 
		# msg.attach(p) 
		  
		# # creates SMTP session 
		# s = smtplib.SMTP('smtp.gmail.com', 587) 
		  
		# # start TLS for security 
		# s.starttls() 
		  
		# # Authentication 
		# s.login(fromaddr, "dot1235AAA") 
		  
		# # Converts the Multipart msg into a string 
		# text = msg.as_string() 
		  
		# # sending the mail 
		# s.sendmail(fromaddr, toaddr, text) 
		  
		# # terminating the session 
		# s.quit() 

