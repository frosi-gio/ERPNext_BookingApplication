# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals,print_function
import frappe
from datetime import datetime, timedelta
import pytz
from frappe.utils import flt, cint, cstr, add_days, getdate, get_datetime, get_time
from frappe import _
import frappe.defaults
import pickle
import os.path
import inspect
from frappe.utils import get_request_site_address
import requests
import googleapiclient.discovery
import google.oauth2.credentials
#from google_auth_oauthlib.flow import InstalledAppFlow
#from google.auth.transport.requests import Request
#from oauth2client import file,client,tools
from frappe.model.mapper import get_mapped_doc
import re
import dns.resolver
import json

	
# Google calendar setup global variables.
redirect_uri = cstr(frappe.utils.get_url())+"?cmd=booking.booking.event.google_callback"
SCOPES = 'https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/calendar.events'
client_id = frappe.db.get_value("Booking Settings", None, "client_id")
client_secret = frappe.db.get_value("Booking Settings", None, "client_secret")
refresh_token = frappe.db.get_value("Booking Settings", None, "refresh_token")
calendar_id = frappe.db.get_value("Booking Settings", None, "calendar_id")

def validate(doc, method):
	# if not doc.customer_contact:
	# 	primary_contact_url = str(frappe.utils.get_url()) + "/desk#List/Customer/" + str(doc.customer)
	# 	frappe.throw("Customer Email and Mobile No both are required. Please also add it into customer PRIMARY CONTACT DETAIL if not added : <a target = '_blank' href=" + "'" + str(primary_contact_url) + "'" +">"+ str(primary_contact_url) +"</a>")
	# frappe.msgprint(cstr(frappe.utils.get_url()))

	# send_event_summary_mail()
	doc.subject = cstr(doc.customer) + " [" + cstr(doc.service) + " by " + cstr(doc.barber_beautician_name) + "]"
	
	send_email(doc)
	#set start date
	start_date = get_datetime(cstr(doc.appointment_date) + " " + cstr(doc.appointment_time))
	doc.starts_on = start_date
	#set end date
	end_date = get_datetime(get_datetime(doc.starts_on) + timedelta(minutes=flt(doc.duration)))
	doc.ends_on = end_date

	# frappe.throw(str(frappe.db.get_value("Event",{"starts_on":start_date,"barber_beautician":doc.barber_beautician},"name")))
	
	#set price list by employee pos profile
	pos_selling_price_list = frappe.db.get_value("POS Profile", {"employee":doc.barber_beautician}, "selling_price_list")
	if hasattr(doc, '__islocal'):
		doc.price_list = pos_selling_price_list

	if not len(doc.event_detail):
		event_detail = doc.append('event_detail', {})
		event_detail.item_code = doc.service
		event_detail.qty = flt(1)

	if doc.barber_beautician:
		if not doc.pos_profile:
			pos_profile = frappe.db.get_value("POS Profile", {"employee":doc.barber_beautician}, "name")
			doc.pos_profile = pos_profile
			frappe.db.set_value("Event", doc.name, "pos_profile", pos_profile)
			frappe.db.commit()
			
	style_dict = {"Opened":"#7575ff","Cancelled":"#ff4d4d","Approved":"#6be273"}

	doc.color = style_dict[doc.workflow_state]
	frappe.db.set_value("Event", doc.name, "color", style_dict[doc.workflow_state])

	if doc.workflow_state == "Approved":
		access_token = get_access_token()
		if access_token:
		# Insert event in google calendar
			created_calendar_event = insert_events(doc,access_token)
			if created_calendar_event:
				doc.google_event_id = created_calendar_event["id"]
				frappe.db.set_value("Event", doc.name, "google_event_id", created_calendar_event["id"])
				frappe.db.commit()

				gcalendar_event_link = "<a href='"+ cstr(created_calendar_event["htmlLink"]) +"' target='_blank'>"+ cstr(created_calendar_event["htmlLink"]) +"</a>"

				doc.google_calendar_event_url = gcalendar_event_link
				frappe.db.set_value("Event", doc.name, "google_calendar_event_url", gcalendar_event_link)
				frappe.db.commit()

	# if doc.workflow_state == "Cancelled":
	# 	access_token = get_access_token()
	# 	credentials_dict = {
	# 	'token': access_token,
	# 	'refresh_token': refresh_token,
	# 	'token_uri': 'https://www.googleapis.com/oauth2/v4/token',
	# 	'client_id': client_id,
	# 	'client_secret': client_secret,
	# 	'scopes':SCOPES
	# 	}
	# 	credentials = google.oauth2.credentials.Credentials(**credentials_dict)
	# 	gcalendar = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
	# 	gcalendar.events().delete(calendarId=calendar_id, eventId=doc.google_event_id).execute()


def after_delete(doc, method):
	access_token = get_access_token()
	credentials_dict = {
	'token': access_token,
	'refresh_token': refresh_token,
	'token_uri': 'https://www.googleapis.com/oauth2/v4/token',
	'client_id': client_id,
	'client_secret': client_secret,
	'scopes':SCOPES
	}
	credentials = google.oauth2.credentials.Credentials(**credentials_dict)
	gcalendar = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
	gcalendar.events().delete(calendarId=calendar_id, eventId=doc.google_event_id).execute()

def after_insert(doc, method):
	pass
	# Get access token
	
	# access_token = get_access_token()
	# if access_token:
	# 	# Insert event in google calendar
	# 	created_calendar_event = insert_events(doc,access_token)
	# 	if created_calendar_event:
	# 		doc.google_event_id = created_calendar_event["id"]
	# 		frappe.db.set_value("Event", doc.name, "google_event_id", created_calendar_event["id"])
	# 		frappe.db.commit()

	# 		gcalendar_event_link = "<a href='"+ cstr(created_calendar_event["htmlLink"]) +"' target='_blank'>"+ cstr(created_calendar_event["htmlLink"]) +"</a>"

	# 		doc.google_calendar_event_url = gcalendar_event_link
	# 		frappe.db.set_value("Event", doc.name, "google_calendar_event_url", gcalendar_event_link)
	# 		frappe.db.commit()

@frappe.whitelist()			
def cancel_request(doc,appointment_date,name, cancel_reason):
	#frappe.msgprint(cstr(doc))
	doc = frappe.get_doc(json.loads(doc))
	#frappe.msgprint(cstr(doc.workflow_state))
	#doc.workflow_state = 'Cancelled'
	#frappe.throw(cstr(doc))
	#frappe.msgprint(doc.employee_email)
	#frappe.msgprint(cstr(doc.workflow_state))
	#frappe.throw(doc.customer_email)
	
	from datetime import date
	
	if getdate(appointment_date) < date.today():
		frappe.throw("You Cannot Cancel Past Date Appointment")
	else:	
		style_dict = {"Opened":"#7575ff","Cancelled":"#ff4d4d","Approved":"#6be273"}
		
		frappe.db.set_value("Event", name, "color", style_dict["Cancelled"])
		frappe.db.set_value("Event", name, 'cancel_reason', cancel_reason)
		frappe.db.set_value("Event", name, 'workflow_state', 'Cancelled')
		frappe.db.commit()
		send_email(doc,flag="2")

def get_access_token():
	if not refresh_token:
		raise frappe.ValidationError(_("GCalendar is not configured."))
	data = {
		'client_id': client_id,
		'client_secret': client_secret,
		'refresh_token': refresh_token,
		'grant_type': "refresh_token",
		'scope': SCOPES
	}
	try:
		r = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data).json()
	except requests.exceptions.HTTPError:
		frappe.throw(_("Something went wrong during the token generation. Please request again an authorization code."))
	if r.get('access_token'):
		frappe.db.set_value("Booking Settings", None, "access_token", cstr(r.get('access_token')))
		frappe.db.commit()
	return r.get('access_token')

def delete_event(access_token):
	credentials_dict = {
	'token': access_token,
	'refresh_token': refresh_token,
	'token_uri': 'https://www.googleapis.com/oauth2/v4/token',
	'client_id': client_id,
	'client_secret': client_secret,
	'scopes':SCOPES
	}
	credentials = google.oauth2.credentials.Credentials(**credentials_dict)
	gcalendar = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
	gcalendar.events().delete(calendarId='primary', eventId=doc.google_event_id).execute()

def insert_events(doc,access_token):
	
	time_zone = cstr(pytz.timezone(frappe.db.get_value("System Settings",None,"time_zone")).localize(get_datetime(doc.starts_on)).strftime('%z'))[:3]+':'+cstr(pytz.timezone(frappe.db.get_value("System Settings",None,"time_zone")).localize(get_datetime(doc.starts_on)).strftime('%z'))[3:]
	start=cstr(doc.starts_on.strftime('%Y-%m-%dT%H:%M:%S'))+time_zone
	end=cstr(doc.ends_on.strftime('%Y-%m-%dT%H:%M:%S'))+time_zone
	credentials_dict = {
	'token': access_token,
	'refresh_token': refresh_token,
	'token_uri': 'https://www.googleapis.com/oauth2/v4/token',
	'client_id': client_id,
	'client_secret': client_secret,
	'scopes':SCOPES
	}
	
	

	credentials = google.oauth2.credentials.Credentials(**credentials_dict)
	gcalendar = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
	
	
	if check_email(cstr(doc.customer_email)):
		# frappe.msgprint('if')
		attendees = [{'email': cstr(doc.customer_email),'self':True}]
	else:
		# frappe.msgprint('else')
		attendees = None
	
	event = {
	'summary': cstr(frappe.db.get_value("Global Defaults",None,"default_company")),
	'location': cstr(frappe.db.get_value("Global Defaults",None,"default_company"))+','+cstr(doc.location),
	'description': 'Your apointment with {} of service {}.Customer Detail Email : {} & Mobile : {}'.format(cstr(doc.barber_beautician_name),cstr(doc.service),cstr(doc.customer_email),cstr(doc.customer_contact)),
	'start': {
		# 'dateTime': start,
		'dateTime': start,
		'timeZone': frappe.db.get_value("System Settings",None,"time_zone")
	},
	'end': {
		# 'dateTime': end,
		'dateTime': end,
		'timeZone': frappe.db.get_value("System Settings",None,"time_zone")
	},
	'attendees': attendees
	}
	
	try:
		
		remote_event = gcalendar.events().insert(calendarId=calendar_id, body=event).execute()
		return remote_event
	except Exception:
		frappe.msgprint("in except")
		frappe.log_error(frappe.get_traceback(), "Google Calendar Synchronization Error")

@frappe.whitelist()
def google_callback(code=None):

	if code is None:
		return {
			'url': 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&response_type=code&prompt=consent&client_id={}&include_granted_scopes=true&scope={}&redirect_uri={}'.format(client_id, SCOPES, redirect_uri)
			}
	else:
		try:
			data = {'code': code,
				'client_id': client_id,
				'client_secret': client_secret,
				'redirect_uri': redirect_uri,
				'grant_type': 'authorization_code'}
			r = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data).json()
			
			frappe.db.set_value("Booking Settings", None, "code", code)
			frappe.msgprint(cstr(r))
			if 'access_token' in r:
				pass
				frappe.db.set_value("Booking Settings", None, "access_token", r['access_token'])
			if 'refresh_token' in r:
				pass
				frappe.db.set_value("Booking Settings", None, "refresh_token", r['refresh_token'])
			frappe.db.commit()
			frappe.local.response["type"] = "redirect"
			frappe.local.response["location"] = "success.html"
			return
		except Exception as e:
			frappe.throw(e.__traceback__)


# Get available timeslot by employee and date.
@frappe.whitelist(allow_guest = True)
def get_availability_data(date, barber_beautician, service):
	"""
	Get availability data of 'Barber / Beautician' on 'date'
	:param date: Date to check in schedule
	:param barber_beautician: Name of the Barber / Beautician
	:param service: Duration of service
	:return: dict containing a list of available slots, list of appointments and duration of service
	"""

	date = getdate(date)
	weekday = date.strftime("%A")

	available_slots = []
	barber_beautician_schedule_name = None
	barber_beautician_schedule = None
	service_durations = None
	branch_holiday_name = None
	barber_beautician_holiday_name = None

	# if branch holiday return
	employee_branch = frappe.db.get_value("Employee", barber_beautician, "branch")
	branch_holiday_name = frappe.db.get_value("Branch", employee_branch, "default_holiday_list")
	if branch_holiday_name:
		branch_holidays = frappe.get_doc("Holiday List", branch_holiday_name)

		if branch_holidays:
			for t in branch_holidays.holidays:
				if t.holiday_date == date:
					frappe.msgprint(_("Barber not available on <b>{0}</b> as it's a <b>Holiday</b>").format(datetime.strptime(cstr(date), '%Y-%m-%d').strftime('%d-%m-%Y')), _('Holiday'), 'red')

	# if barber holiday return
	barber_beautician_holiday_name = frappe.db.get_value("Employee", barber_beautician, "holiday_list")
	if barber_beautician_holiday_name:
		barber_beautician_holidays = frappe.get_doc("Holiday List", barber_beautician_holiday_name)

		if barber_beautician_holidays:
			for t in barber_beautician_holidays.holidays:
				if t.holiday_date == date:
					frappe.msgprint(_("Barber not available on <b>{0}</b> as it's a <b>Holiday</b>").format(datetime.strptime(cstr(date), '%Y-%m-%d').strftime('%d-%m-%Y')), _('Holiday'), 'red')

	# if employee on leave return
	leave_application_list = frappe.db.sql("""SELECT * FROM `tabLeave Application` WHERE `tabLeave Application`.status = 'Approved' AND `tabLeave Application`.employee = %s AND (%s BETWEEN `tabLeave Application`.from_date AND `tabLeave Application`.to_date)""" ,(cstr(barber_beautician), cstr(date)),as_dict = 1)

	if leave_application_list and len(leave_application_list) > 0:
		frappe.msgprint(_("Barber is on leave on <b>{0}</b>. Please select another day or change the barber.").format(datetime.strptime(cstr(date), '%Y-%m-%d').strftime('%d-%m-%Y')), _('On Leave'), 'red')

	# get barber's schedule
	barber_beautician_schedule_name = frappe.db.get_value("Employee", barber_beautician, "daily_schedule_list")
	if barber_beautician_schedule_name:
		barber_beautician_schedule = frappe.get_doc("Employee Schedule", barber_beautician_schedule_name)
		service_durations = frappe.db.get_value("Item", service, "service_duration")
	else:
		frappe.throw(_("Barber {0} does not have a Employee Schedule. Add it in Employee master".format(barber_beautician)))

	if barber_beautician_schedule:
		for t in barber_beautician_schedule.time_slots:
			if weekday == t.day:
				dict_to_append = {"day":str(t.day),"from_time":str(t.from_time), "to_time":str(t.to_time), "from_time_to_decimal":TimeToDecimal(str(t.from_time))}
				available_slots.append(dict_to_append)

	if not service_durations:
		frappe.throw(_('"Service Duration" hasn"t been set for <b>{0}</b>. Add it in Item master.').format(service))

	# if employee not available return
	if not available_slots:
		# TODO: return available slots in nearby dates
		frappe.throw(_("Barber not available on {0}").format(weekday))

	sorted_available_slots = sorted(available_slots, key= lambda k: flt(k['from_time_to_decimal']))

	# get appointments on that day for employee
	appointments = frappe.get_all(
		"Event",
		filters=[["barber_beautician", "=", barber_beautician], ["appointment_date","=", date], ["workflow_state", "in", ('Approved','Opened') ]],
		fields=["name", "appointment_time", "duration", "workflow_state"])

	return {
		"available_slots": sorted_available_slots,
		"appointments": appointments,
		"duration_of_service": service_durations
	}

@frappe.whitelist()
def TimeToDecimal(time):
	(h, m, s) = str(time).split(':')

	if '.' in str(s):
		s = str(s).split('.')
		result = int(h) * 60 + int(m) + int(s[0])/60
	else:
		result = int(h) * 60 + int(m) + int(s)/60

	return str(flt(result)/60)

# Get end time of the day for barber.
@frappe.whitelist()
def get_day_end_time(date, barber_beautician):
	"""
	Get end time of 'Barber / Beautician' on 'date'
	:param date: Date to check in schedule
	:param barber_beautician: Name of the Barber / Beautician
	:return: end time of the given date
	"""
	barber_beautician_schedule_name = frappe.db.get_value("Employee", barber_beautician, "daily_schedule_list")
	date = getdate(date)
	weekday = date.strftime("%A")
	
	get_end_time = frappe.db.sql("""SELECT Max(`tabEmployee Schedule Time Slot`.to_time) as day_end_time FROM `tabEmployee Schedule` LEFT JOIN `tabEmployee Schedule Time Slot` ON `tabEmployee Schedule`.name = `tabEmployee Schedule Time Slot`.parent WHERE `tabEmployee Schedule`.name = %s AND `tabEmployee Schedule Time Slot`.day = %s""" ,(cstr(barber_beautician_schedule_name),cstr(weekday)),as_dict = 1)
	if get_end_time and len(get_end_time) > 0:
		return cstr(get_end_time[0]['day_end_time'])

# Get end time of the day for barber.
@frappe.whitelist()
def get_lunch_start_time(date, barber_beautician):
	"""
	Get lunch start time of 'Barber / Beautician' on 'date'
	:param date: Date to check in schedule
	:param barber_beautician: Name of the Barber / Beautician
	:return: lunch start time of the given date
	"""
	barber_beautician_schedule_name = frappe.db.get_value("Employee", barber_beautician, "daily_schedule_list")
	date = getdate(date)
	weekday = date.strftime("%A")
	
	get_lunch_start_time = frappe.db.sql("""SELECT `tabEmployee Schedule Time Slot`.to_time as lunch_start_time FROM `tabEmployee Schedule` LEFT JOIN `tabEmployee Schedule Time Slot` ON `tabEmployee Schedule`.name = `tabEmployee Schedule Time Slot`.parent WHERE `tabEmployee Schedule`.name = %s AND `tabEmployee Schedule Time Slot`.day = %s AND `tabEmployee Schedule Time Slot`.is_lunch_time = 1""" ,(cstr(barber_beautician_schedule_name),cstr(weekday)),as_dict = 1)

	if get_lunch_start_time and len(get_lunch_start_time) > 0:

		return cstr(get_lunch_start_time[0]['lunch_start_time'])

@frappe.whitelist()
def send_email(doc,flag=1):
	#frappe.msgprint(cstr(flag))
	if cstr(flag) == "2":
		doc.workflow_state = "Cancelled"
		#frappe.throw(cstr(doc.workflow_state))

	customer_email = doc.customer_email
	employee_email = doc.employee_email
	
	if doc.workflow_state == "Opened":
		
		if customer_email:
			msg = 'Dear {0},<br/> This is a confirmation that you have temporarily booked {1} on {2} at {3} with {4} at {5}.<br/>We will shortly contact you by email to confirm your chosen appointment.<br/>Thank you for choosing Antonios Barber Shop.<br/><b>{6}</b><br/><b>{7}</b><br/><b>{8}</b>'.format(cstr(doc.customer), cstr(doc.service), cstr(doc.appointment_date),cstr(doc.appointment_time), cstr(doc.barber_beautician_name), cstr(doc.location), cstr(doc.company), cstr(frappe.db.get_value("Company",str(doc.company), "phone_no")), cstr(frappe.db.get_value("Company",str(doc.company), "website")))
		
			frappe.sendmail(recipients=customer_email,
			subject="Antonio Barber Pending appointment",
			message=str(''.join([i if ord(i) < 128 else ' ' for i in msg])),
			now=True)

		if employee_email:	
			msg = 'Hello,<br/>You have new booking.<br/><b>Service: </b>{0}<br/><b>Date: </b>{1}<br/><b>Time: </b>{2}<br/><b>Client name: </b>{3}<br/><b>Client phone: </b>{4}<br/><b>Client email: </b>{5}'.format(str(doc.service),str(doc.appointment_date), str(doc.appointment_time), str(doc.customer), str(doc.customer_contact),str(doc.customer_email))

			frappe.sendmail(recipients=employee_email,
			subject="Antonio Barber Pending appointment",
			message=str(''.join([i if ord(i) < 128 else ' ' for i in msg])),
			now=True)

	if doc.workflow_state == "Approved":

		if customer_email:
			msg = 'Dear {0},<br/>This is a confirmation that your appointment for  {1} has been approved.<br/>We will be looking forward to see you at {2} on {3} at {4}.<br/>Should you wish to cancel your appointment , please call at the shop or cancel it by login on our website.<br/><b>{5}</b><br/><b>{6}</b><br/><b>{7}</b><br/>'.format(str(doc.customer), str(doc.service), str(doc.location), str(doc.appointment_date), str(doc.appointment_time), str(doc.company), str(frappe.db.get_value("Company",str(doc.company), "phone_no")), str(frappe.db.get_value("Company",str(doc.company), "website")))

			frappe.sendmail(recipients=customer_email,
			subject="Antonio Barber appointment approved",
			message=str(''.join([i if ord(i) < 128 else ' ' for i in msg])),
			now=True)

		if employee_email:	
			msg = 'Hello,<br/>A Booking has been Confirmed.<br/><b>Service: </b>{0}<br/><b>Date: </b>{1}<br/><b>Time: </b>{2}<br/><b>Client name: </b>{3}<br/><b>Client phone: </b>{4}<br/><b>Client email: </b>{5}'.format(str(doc.service),str(doc.appointment_date), str(doc.appointment_time), str(doc.customer), str(doc.customer_contact), str(doc.customer_email))

			frappe.sendmail(recipients=employee_email,
			subject="Antonio Barber appointment approved",
			message=str(''.join([i if ord(i) < 128 else ' ' for i in msg])),
			now=True)

	if doc.workflow_state == "Cancelled":
		if customer_email:
			msg='Dear {0},<br/>You have cancelled your appointment of {1} on {2} at {3}.<br/>Hope to be of service to you in the near future.<br/><b>{4}</b><br/><b>{5}</b><br/><b>{6}</b><br/>'.format(str(doc.customer), str(doc.service), str(doc.appointment_date), str(doc.appointment_time), str(doc.company), str(frappe.db.get_value("Company",str(doc.company), "phone_no")), str(frappe.db.get_value("Company",str(doc.company), "website")))

			frappe.sendmail(recipients=customer_email,
			subject="Antonio Barber appointment Cancelled",
			message=str(''.join([i if ord(i) < 128 else ' ' for i in msg])),
			now=True)

		if employee_email:
			msg = 'Hello,<br/>The following booking has been cancelled.<br/><b>Service: </b>{0}<br/><b>Date: </b>{1}<br/><b>Time: </b>{2}<br/><b>Client name: </b>{3}<br/><b>Client phone: </b>{4}<br/><b>Client email: </b>{5}'.format(str(doc.service),str(doc.appointment_date), str(doc.appointment_time), str(doc.customer), str(doc.customer_contact), str(doc.customer_email))

			frappe.sendmail(recipients=employee_email,
			subject="Antonio Barber appointment Cancelled",
			message=str(''.join([i if ord(i) < 128 else ' ' for i in msg]))	,
			now=True)

# ---------------------------------------------------------------------------
# E mail tomorrows agenda to the employee
# --------------------------------------------------------------------------- */	
def send_event_summary_mail():
	from datetime import date
	tomorrow = date.today() + timedelta(1)
	tomorrow_event = frappe.get_all('Event', filters={'appointment_date':tomorrow}, fields=['customer', 'barber_beautician_name','service','starts_on','ends_on','appointment_date','location'])
	i=1
	event_string_concated = ''
	for event in tomorrow_event:
		event_string = '<br/><br/>{}. <b>{}</b> of customer-<b>{}</b> by Service provider-<b>{}</b> which will starts on <b>{}</b> and ends on <b>{}</b> at location-<b>{}</b>'.format(cstr(i),cstr(event['service']),cstr(event['customer']),cstr(event['barber_beautician_name']),cstr(event['starts_on']),cstr(event['ends_on']),cstr(event['location']))
		event_string_concated = event_string_concated + event_string
		i+=1
	
	sys_manager_user = frappe.get_all('User', filters={'role_profile_name':'System Manager'}, fields=['email','first_name'])
	for mail in sys_manager_user:
		frappe.sendmail(
			recipients=cstr(mail['email']),
			subject='Tommorow Agenda',
			message="Dear {},<br/>Here is the summary of your tommorow's agenda.{}".format(cstr(mail['first_name']),event_string_concated))

# ---------------------------------------------------------------------------
# Mapping Event to sales invoice
#
# NOTE: We have make Event Detail child table here to map the item with Sales Invoice Item as doctype field to child table field mapping is not possible.
# --------------------------------------------------------------------------- */
@frappe.whitelist()		
def make_invoice(source_name, target_doc=None, ignore_permissions=False):
	
	def postprocess(source, target):
		pass

	def set_missing_values(source, target):
		pass

	def update_item(source, target, source_parent):
		pass

	doclist = get_mapped_doc("Event", source_name, {
		"Event": {
			"doctype": "Sales Invoice",
			"field_map": {
				"customer": "customer",
				"location":"territory",
				"appointment_date":"posting_date",
				"appointment_time":"posting_time",
				"appointment_date":"due_date",
				"pos_profile":"pos_profile",
				"is_pos":"is_pos",
				"price_list":"selling_price_list",
				"name":"event_id"
			},
			"validation": {
				"workflow_state": ["=", "Approved"]
			},
			"condition":lambda doc: doc.sales_invoice != None or doc.sales_invoice != ''
		},
		"Event Detail": {
			"doctype": "Sales Invoice Item",
			"field_map": {
				"item_code": "item_code",
				"qty": "qty"
			}
		}
	}, target_doc, postprocess, ignore_permissions=ignore_permissions)

	return doclist


def check_email(email):
    match_grp = re.match(r'(.*)@(.*)', email)
    try:
        records = dns.resolver.query(match_grp.group(2), 'MX')
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)
        print(mxRecord)
        searchObj = re.search( r'google', mxRecord)
        if searchObj != None:
            return True
        else:
            return False
    except:
        frappe.msgprint("<b>Calendar Event</b> cannot be set as <b>customer email</b> is not proper/Unavailable.")

@frappe.whitelist()
def get_wordpress_url():
    return cstr(frappe.get_value("Booking Settings",None,"customer_api"))