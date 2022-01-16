# Copyright (c) 2013, August Infotech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, cstr, add_days, getdate, get_datetime, get_time

def execute(filters=None):
	columns, data = [], []
	columns = get_columns(filters)

	get_data_list = get_todo_list(filters)

	for d in get_data_list:
		data.append([d.starts_on, d.ends_on, d.location, d.customer, d.service, d.barber_beautician, d.barber_beautician_name, d.workflow_state])

	return columns, data

def get_columns(filters):
	"""return columns based on filters"""
	columns = [
		{
			"label": _("Start Time"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("End Time"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Location"),
			"fieldname": "location",
			"fieldtype": "Link",
			"options": "Territory",
			"width": 100
		},
		{
			"label": _("Customer"),
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 100
		},
		{
			"label": _("Service"),
			"fieldname": "service",
			"fieldtype": "Link",
			"options": "Item",
			"width": 100
		},
		{
			"label": _("Employee"),
			"fieldname": "employee",
			"fieldtype": "Link",
			"options": "Employee",
			"width": 100
		},
		{
			"label": _("Employee Name"),
			"fieldname": "employee_name",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": _("Status"),
			"fieldname": "status",
			"fieldtype": "Data",
			"width": 100
		}
	]
	return columns

def get_todo_list(filters):
	today_date = getdate(frappe.utils.today())
	tomorrow_date = add_days(today_date,1)
	tomorrow_schedule = frappe.get_all('Event', filters={'appointment_date':str(tomorrow_date)}, fields=['starts_on','ends_on', 'location', 'customer','service','barber_beautician','barber_beautician_name','workflow_state'])

	return tomorrow_schedule
