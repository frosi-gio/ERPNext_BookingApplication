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
		data.append([d.date, d.reference_type, d.reference_name, d.assigned_by, d.owner])

	return columns, data

def get_columns(filters):
	"""return columns based on filters"""
	columns = [
		{
			"label": _("Date"),
			"fieldname": "date",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": _("Reference Type"),
			"fieldname": "reference_type",
			"width": 110
		},
		{
			"label": _("Reference Name"),
			"fieldname": "reference_name",
			"fieldtype": "Dynamic Link",
			"options": "reference_type",
			"width": 120
		},
		{
			"label": _("Assigned By"),
			"fieldname": "assigned_by",
			"fieldtype": "Link",
			"options": "User",
			"width": 100
		},
		{
			"label": _("Allocated To"),
			"fieldname": "allocated_to",
			"fieldtype": "Link",
			"options": "User",
			"width": 100
		}
	]
	return columns

def get_todo_list(filters):
	today_date = getdate(frappe.utils.today())
	tomorrow_date = add_days(today_date,1)
	tomorrow_schedule = frappe.get_all('ToDo', filters={'date':str(tomorrow_date)}, fields=['reference_name', 'reference_type', 'assigned_by','date','owner'])

	return tomorrow_schedule
