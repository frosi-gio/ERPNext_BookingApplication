# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals,print_function
import frappe
from datetime import datetime, timedelta
from frappe.utils import flt, cint, cstr, add_days, getdate, get_datetime, get_time
from frappe import _
import frappe.defaults
from frappe import _
import pickle
import os.path
import inspect
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
# from google.auth.transport import requests
from oauth2client import file,client,tools


def validate(doc, method):
	set_google_calender_event()
	send_email(doc)
	#set start date
	start_date = get_datetime(cstr(doc.appointment_date) + " " + cstr(doc.appointment_time))
	doc.starts_on = start_date
	#set end date
	end_date = cstr(get_datetime(doc.starts_on) + timedelta(minutes=flt(doc.duration)))
	doc.ends_on = end_date
	



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
					frappe.msgprint(_("Barber / Beautician not available on <b>{0}</b> as it's a <b>Holiday</b>").format(datetime.strptime(cstr(date), '%Y-%m-%d').strftime('%d-%m-%Y')), _('Holiday'), 'red')

	# if barber holiday return
	barber_beautician_holiday_name = frappe.db.get_value("Employee", barber_beautician, "holiday_list")
	if barber_beautician_holiday_name:
		barber_beautician_holidays = frappe.get_doc("Holiday List", barber_beautician_holiday_name)

		if barber_beautician_holidays:
			for t in barber_beautician_holidays.holidays:
				if t.holiday_date == date:
					frappe.msgprint(_("Barber / Beautician not available on <b>{0}</b> as it's a <b>Holiday</b>").format(datetime.strptime(cstr(date), '%Y-%m-%d').strftime('%d-%m-%Y')), _('Holiday'), 'red')

	# if employee on leave return
	leave_application_list = frappe.db.sql("""SELECT * FROM `tabLeave Application` WHERE `tabLeave Application`.status = 'Approved' AND `tabLeave Application`.employee = %s AND (%s BETWEEN `tabLeave Application`.from_date AND `tabLeave Application`.to_date)""" ,(cstr(barber_beautician), cstr(date)),as_dict = 1)

	if leave_application_list and len(leave_application_list) > 0:
		frappe.msgprint(_("Barber / Beautician is on leave on <b>{0}</b>. Please select another day or change the barber.").format(datetime.strptime(cstr(date), '%Y-%m-%d').strftime('%d-%m-%Y')), _('On Leave'), 'red')

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
				available_slots.append(t)

	if not service_durations:
		frappe.throw(_('"Service Duration" hasn"t been set for <b>{0}</b>. Add it in Item master.').format(service))

	# if employee not available return
	if not available_slots:
		# TODO: return available slots in nearby dates
		frappe.throw(_("Barber / Beautician not available on {0}").format(weekday))

	# get appointments on that day for employee
	appointments = frappe.get_all(
		"Event",
		filters=[["barber__beautician", "=", barber_beautician], ["appointment_date","=", date], ["workflow_state", "in", ('Approved','Opened') ]],
		fields=["name", "appointment_time", "duration", "workflow_state"])

	return {
		"available_slots": available_slots,
		"appointments": appointments,
		"duration_of_service": service_durations
	}

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

@frappe.whitelist()
def send_email(doc):
	customer_email = frappe.db.get_value("Customer",doc.customer,"email_id")
	employee_email = frappe.db.get_value("Employee",doc.barber__beautician,"personal_email")
	
	if doc.workflow_state == "Opened":
		frappe.sendmail(recipients=customer_email,
		subject="Antonio Barber Pending appointment",
		message="Dear {}, Your appointment with Antonio Barber is under review.You will notify after it will accept".format(doc.customer))
		frappe.sendmail(recipients=employee_email,
		subject="Antonio Barber Pending appointment",
		message="Hello,new appointment-{} has been created and its in pending state.Please review it".format(doc.name))

	if doc.workflow_state == "Approved":
		frappe.sendmail(recipients=customer_email,
		subject="Antonio Barber appointment approved",
		message="Dear {}, Your appointment with Antonio Barber is approved.".format(doc.customer))
		frappe.sendmail(recipients=employee_email,
		subject="Antonio Barber appointment approved",
		message="Hello,new appointment-{} has been approved.".format(doc.name))

	if doc.workflow_state == "Cancelled":
		frappe.sendmail(recipients=customer_email,
		subject="Antonio Barber appointment Cancelled",
		message="Dear {}, Your appointment with Antonio Barber is cancelled.Sorry for inconvinience".format(doc.customer))
		frappe.sendmail(recipients=employee_email,
		subject="Antonio Barber appointment Cancelled",
		message="Hello,new appointment-{} has been cancelled.".format(doc.name))


@frappe.whitelist()
def set_google_calender_event():
	creds = None
	SCOPES = ['https://www.googleapis.com/auth/calendar']
	CLIENT_SECRET_FILE = 'credentials.json'
	APPLICATION_NAME = 'Antonio Barber'
	event_object = {
	'summary': 'Antonio barber appointment',
	'location': 'Antonio barber shop',
	'description': 'Be ready to reinvent your style',
	'start': {
		'dateTime': '2019-02-05T09:00:00+05:30',
		'timeZone': 'Asia/Kolkata',
	},
	'end': {
		'dateTime': '2019-02-05T09:30:00+05:30',
		'timeZone': 'Asia/Kolkata',
	},
	'attendees': [
		{'email': 'raj.tailor@augustinfotechteam.com'}
	],
	'reminders': {
		'useDefault': False,
		'overrides': [
		{'method': 'email', 'minutes': 24 * 60},
		{'method': 'popup', 'minutes': 10},
		],
	},
	}
	
	# try:
	# 	import argparse		
	# 	flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
	# except ImportError:
	# 	flags = None
		
	
	
	if os.path.exists('token.pickle'):
		with open('token.pickle', 'rb') as token:
			creds = pickle.load(token)
	
	if not creds or not creds.valid:
		frappe.msgprint("in-fun0")
		frappe.msgprint(cstr(creds))
		if not creds:
			directory_path = frappe.get_site_path('public', 'credentials')
			cred_file_path = os.path.join(cstr(directory_path), cstr('credentials.json'))
			
			flow = InstalledAppFlow.from_client_secrets_file(cred_file_path, SCOPES)
			# frappe.throw("Hello 3")
			creds = flow.run_local_server()
			frappe.throw("Hello 4")
        else:
			frappe.msgprint("in-fun2")	
			creds.refresh(Request())
			frappe.msgprint("in-fun1")
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
	
	service = build('calendar', 'v3', credentials=creds)
	event = service.events().insert(calendarId='primary', body=event_object).execute()
	frappe.msgprint('Event created: {}'.format((event.get('htmlLink'))))
	

	
