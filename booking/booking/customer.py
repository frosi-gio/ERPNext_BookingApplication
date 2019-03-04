from __future__ import unicode_literals,print_function
import frappe
from datetime import datetime, timedelta
import pytz
from frappe.utils import flt, cint, cstr, add_days, getdate, get_datetime, get_time
from frappe import _
import frappe.defaults
import requests

@frappe.whitelist()
def save_customer_password(doc_name,password,user_id):
    
    frappe.db.set_value("Customer",doc_name,"customer_password",password)
    frappe.db.set_value("Customer",doc_name,"website_userid",user_id)
    frappe.db.commit()
    frappe.sendmail(
    recipients=frappe.db.get_value("Customer",doc_name,"email_id"),
    subject="Your Login Details",
    message="Dear {},<br/>Your account has been setup,below is your login details<br/>ID : <b>{}</b><br/>Password : <b>{}</b>".format(frappe.db.get_value("Customer",doc_name,"customer_name"),frappe.db.get_value("Customer",doc_name,"email_id"),password))
    customer_doc=frappe.get_doc("Customer",doc_name,"name")
    customer_doc.flags.ignore_permissions = True
    customer_doc.save()

@frappe.whitelist()
def get_wordpress_url():
    return cstr(frappe.get_value("Booking Settings",None,"customer_api"))
    

