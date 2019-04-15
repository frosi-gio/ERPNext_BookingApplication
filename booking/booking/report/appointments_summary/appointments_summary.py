# Copyright (c) 2013, August Infotech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, cstr, add_days, getdate, get_datetime, get_time,today


def execute(filters=None):
	columns, data = [], []
	time_dict = {}
	
	
	barber = []
	booked_time_slots = [] 
	event_summary =[]
	columns = get_columns(filters)
	time_row=[]
	event_time = frappe.get_all("Employee Schedule Time Slot",fields=['from_time'])
	time_data = []
	

# -------------------------------get array of all sorted time--------------------------------
	for time in event_time:
		if time.from_time not in time_data:
			time_data.append(time.from_time)

	time_data = sorted(time_data)

# -------------------------------------get time row-----------------------------------------------
	
	for t in range(0,len(time_data)):
		if t == 0:
			time_row.append('')
		time_row.append(cstr(time_data[t]))
	
	data.append(time_row)

# -------------------------------get all barber-----------------------------------------------
	for b in get_barber():
		row1 = []
		for t in range(0,len(time_row)):
			if t == 0:
				row1.append(b)
			row1.append('')
		data.append(row1)

	

# ----------------------------------make time slot dict with index-------------------------------	
	c = 1
	for t in time_data:
		time_dict[TimeToDecimal(t)]=c
		c=c+1
	

# ----------------------------------------ploting data in report------------------------------------------------------
	
	event_data = frappe.get_all("Event",filters=[["workflow_state", "in", ('Approved','Opened')],["appointment_date","=",today()]],fields=['barber_beautician_name','appointment_time','duration','name'],order_by="appointment_time")
	
	for eve in event_data:
		event_summary.append([eve.barber_beautician_name,cstr(eve.appointment_time),eve.name])
		barber.append(eve.barber_beautician_name)
		booked_time_slots.append(eve.appointment_time)

	for aptmnt in event_data:
		start_time = TimeToDecimal(aptmnt.appointment_time)
		end_time = flt(TimeToDecimal(aptmnt.appointment_time)) + flt(aptmnt.duration)/60
		for slot in time_data:
			slot_time = TimeToDecimal(slot)
			if (flt(start_time) <= flt(slot_time)) and (flt(end_time) > flt(slot_time)):				
				for d in range(0,len(data)):
					if cstr(data[d][0]) == cstr(aptmnt.barber_beautician_name):
						data[d][time_dict[TimeToDecimal(slot)]] = cstr(aptmnt.name)
					
    
	new_data = [[data[j][i] for j in range(len(data))] for i in range(len(data[0]))]
	
	new_data = new_data[1:]
	
	return columns, new_data


def get_columns(filters):

	
	columns = [
		{
			"label":_("Event Time"),
			"fieldname": "event_time",
			"fieldtype": "Time",
			"width": 100
		}
	]
	barb = get_barber()

	for b in barb:
		columns.append(
			{
			"label":_(cstr(b)),
			"fieldname": cstr(b),
			"fieldtype": "Link",
			"options": "Event",
			"width": 100	
			}
		)

	return columns

def get_barber():
	barb=[]
	barber_data = frappe.get_all("Employee",filters=[["is_service_provider","=",1]],fields=['employee_name'])
	for bd in barber_data:
		barb.append(cstr(bd.employee_name))

	return barb

def TimeToDecimal(time):
	(h, m, s) = str(time).split(':')

	if '.' in str(s):
		s = str(s).split('.')
		result = int(h) * 60 + int(m) + int(s[0])/60
	else:
		result = int(h) * 60 + int(m) + int(s)/60

	return str(flt(result)/60)
	