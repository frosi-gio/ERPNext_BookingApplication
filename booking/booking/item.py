# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe.utils import flt, cint, cstr, today, getdate, get_datetime, time_diff_in_hours, now
from frappe.model.naming import make_autoname
import json
from frappe import _
import frappe.defaults
from six.moves import urllib
from erpnext.accounts.utils import get_fiscal_year
import requests


 
PRODUCT_API_URL_LIVE=cstr(frappe.db.get_value("Booking Settings",None,"product_api"))

def validate(self,method):
	# frappe.throw(cstr(self))
	if not hasattr(self, '__islocal'):
		add_item_to_employee(self)

	if not hasattr(self, '__islocal'):
		# frappe.msgprint("second time call")
		if PRODUCT_API_URL_LIVE:
			
			add_item_to_wordpress(self)
		
	# Get if the item group is an activity or not.
	is_activity = frappe.db.get_value("Item Group", self.item_group, "is_activity")
	
	# Check if activity type is exist or not.
	activity_name = frappe.db.get_value("Activity Type", self.name, "name")
	
	# Create an activity type if item group is an activity and not exist.
	if is_activity and not activity_name:
		activity_type = frappe.get_doc({
				"doctype":"Activity Type",
				"activity_type":str(self.name)
			})
		activity_type.flags.ignore_permissions = True
		activity_type.insert()

# ---------------------------------------------------------------------------
# Add Item and Item group Into Employee child table , Create Activity cost
# --------------------------------------------------------------------------- */
def add_item_to_employee(self):
	
	if frappe.db.get_value("Item Group", self.item_group, "is_activity"):	
		for emp in self.service_provider:
			#check if services exist in employee or not
			if not frappe.db.get_value("Services", {"parent":cstr(emp.provider),"service":cstr(self.name)}, "name"):
				
				insert_employee = {
					"service":str(self.name),
					"billing_rate":emp.billing_rate,
					"category":str(self.item_group),
					"is_provided":"Yes"
				}
				Employee = frappe.get_doc("Employee",emp.provider)
				Employee.append("services",insert_employee)
				Employee.flags.ignore_permissions = True
				Employee.save()
				frappe.db.commit()

			#if services exist in employee then update service rate
			elif frappe.db.get_value("Services", {"parent":cstr(emp.provider),"service":cstr(self.name)}, "name"):

				services = frappe.get_doc("Services",{"parent":emp.provider, "service":self.name, "is_provided":"Yes"})
				services.billing_rate = emp.billing_rate
				services.save()
				frappe.db.commit()

				Employee = frappe.get_doc("Employee",emp.provider)
				Employee.save()
				frappe.db.commit()

			#check if services type exist in employee or not
			if not frappe.db.get_value("Services Type", {"parent":str(emp.provider),"services":str(self.item_group)}, "name"):
				
				insert_employee_grp = {
					"services":str(self.item_group),
					"is_provided":"Yes"
				}
				Employee = frappe.get_doc("Employee",emp.provider)
				Employee.append("services_type",insert_employee_grp)
				Employee.flags.ignore_permissions = True
				Employee.save()
				frappe.db.commit()
				

			#check if Activity cost exist of employee or not
			if not frappe.db.get_value("Activity Cost", {"employee":emp.provider,"activity_type":self.name}, "name"):					
				enter_activity_cost(self,str(emp.provider),emp.billing_rate,str(self.name))



def enter_activity_cost(self,employee,billing_rate,activity):
	
	activity_cost = frappe.get_doc({
			"doctype":"Activity Cost",
			"activity_type":activity,
			"billing_rate":billing_rate,
			"employee":employee
		})
	activity_cost.flags.ignore_permissions = True
	activity_cost.insert()

@frappe.whitelist()
def update_product_id(self,name,id):
	frappe.db.set_value("Item", name, "website_product_id", id)
	frappe.db.commit()
	item_doc=frappe.get_doc("Item",name,"name")
	item_doc.flags.ignore_permissions = True
	item_doc.save()

@frappe.whitelist()
def get_all_employee():
	employee = frappe.get_all('Employee',filters={'is_service_provider':1},fields=['employee_name','name'])
	
	if employee:
		return employee

def after_insert(self, method):
	add_item_to_employee(self)
	# frappe.msgprint("first time")
	if PRODUCT_API_URL_LIVE:
		
		add_item_to_wordpress(self)
	
	

def add_item_to_wordpress(self):
	
	if self.show_in_website == 1:
		# frappe.msgprint(cstr(PRODUCT_API_URL_LIVE))
		# frappe.msgprint("here1")
		# frappe.msgprint("http://192.168.123.72:5151"+self.image)
		item_grp_string = ''  
		for item in self.website_item_groups:
			item_grp_string = item_grp_string + item.item_group + ","
			# frappe.msgprint(item.item_group)
		data_object = {
        "product_title" : self.item_name,
        "product_sku" : self.name,
		"price":self.standard_rate,
		"product_desc":self.web_long_description,
		"category": item_grp_string[0:len(item_grp_string)-1],
		"product_image":frappe.utils.get_url()+cstr(self.image)
		}

		headers_content = {
        'Content-Type': 'application/json',
    	}
		response_data = requests.post(PRODUCT_API_URL_LIVE,headers=headers_content,data=json.dumps(data_object))
		# update_product_id(self.name, cstr(response_data.json()['product_id']))
		# frappe.msgprint(cstr(response_data.json()['product_id']))
		self.website_product_id = cstr(response_data.json()['product_id'])
		# frappe.show_alert({message:__("Created in website"),indicator:'green'})


def after_delete(self, method):
	if self.show_in_website == 1:
		data_object = {
			
			"product_sku" : [self.name],
			"delete_product":"yes"
		}
		headers_content = {
		'Content-Type': 'application/json',
		}
		response_data = requests.post(PRODUCT_API_URL_LIVE,headers=headers_content,data=json.dumps(data_object))
	# frappe.msgprint(cstr(response_data.text))


	