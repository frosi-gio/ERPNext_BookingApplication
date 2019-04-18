# Copyright (c) 2013, August Infotech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint, cstr, add_days, getdate, get_datetime, get_time,today ,get_url
import json


def execute(filters=None):
	# frappe.throw(json.loads(frappe.new_doc("Event")))
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

# ----------------------------------make time slot dict with index----------------------------------------------------	
	c = 1
	for t in time_data:
		time_dict[TimeToDecimal(t)]=c
		c=c+1
	# frappe.throw(str(time_dict))

	time_str_dict = {}
	c = 1
	for t in time_data:
		time_str_dict[c]=str(t)
		c=c+1
	# frappe.msgprint(str(time_str_dict))

# -------------------------------get all barber----------------------------------------------------------------
	for k,v in get_barber(filters).items():
		row1 = []
		for t in range(0,len(time_row)):
			if t == 0:
				row1.append(v)
			else:
				row1.append("<a target='_blank' href = {0} class='barber' data-barber={1} data-row-index={2} data-row-time ={3}> + New </a>".format(str(frappe.utils.get_url()) + "/desk#Form/Event/New%20Event%201?barber=" + str(k.split("/")[1])+"&date="+str(filters.get("appointment_date"))+"&time="+str(time_str_dict[t]), str(k), str(t), str(time_str_dict[t])))
		data.append(row1)
	

# ----------------------------------------ploting data in report------------------------------------------------------
	
	event_data = frappe.get_all("Event",filters=[["workflow_state", "in", ('Approved','Opened')],["appointment_date","=",filters.get("appointment_date")]],fields=['barber_beautician_name','appointment_time','duration','name','subject','workflow_state'],order_by="appointment_time")
	
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
				#frappe.msgprint(cstr(data))
				for d in range(0,len(data)):
					#frappe.msgprint("hi")
					#frappe.msgprint(cstr(data[d][0]))
					if cstr(data[d][0]) == cstr(aptmnt.barber_beautician_name):
						if aptmnt.workflow_state == "Approved":
							data[d][time_dict[TimeToDecimal(slot)]] = "<a style='background-color: {0};' href={1}/desk#Form/Event/{2}>{3}</a>".format("#9deca2",frappe.utils.get_url(),aptmnt.name,aptmnt.subject)
						elif aptmnt.workflow_state == "Opened":
							data[d][time_dict[TimeToDecimal(slot)]] = "<a style='background-color: {0};' href={1}/desk#Form/Event/{2}>{3}</a>".format("#a3a3ff",frappe.utils.get_url(),aptmnt.name,aptmnt.subject)

					
    
	new_data = [[data[j][i] for j in range(len(data))] for i in range(len(data[0]))]
	# frappe.throw(cstr(new_data))
	
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
	barb = get_barber(filters)

	for k,v in barb.items():
		columns.append(
			{
			"label":_(cstr(v)),
			"fieldname": cstr(v),
			"fieldtype": "Data",
			"width": 160	
			}
		)

	return columns

def get_barber(filters):
	barb={}
	barber_data = frappe.get_all("Employee",filters=[["is_service_provider","=",1],["name","=",filters.get("barber")]],fields=['employee_name','name'])
	for bd in barber_data:
		barb[bd.name] = cstr(bd.employee_name)

	return barb

def TimeToDecimal(time):
	(h, m, s) = str(time).split(':')

	if '.' in str(s):
		s = str(s).split('.')
		result = int(h) * 60 + int(m) + int(s[0])/60
	else:
		result = int(h) * 60 + int(m) + int(s)/60

	return str(flt(result)/60)
	