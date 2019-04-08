from __future__ import unicode_literals,print_function
import frappe
from datetime import datetime, timedelta
import pytz
from frappe.utils import flt, cint, cstr, add_days, getdate, get_datetime, get_time
from frappe import _
import frappe.defaults
import requests
import random
import string
import json

Customer_API_URL_LIVE=cstr(frappe.db.get_value("Booking Settings",None,"customer_api"))

def after_insert(self,method):
    
    create_customer_wordpress(self)
    # frappe.throw("validate")


# @frappe.whitelist()
# def save_customer_password(doc_name,password,user_id):
#     frappe.db.set_value("Customer",doc_name,"customer_password",password)
#     frappe.db.set_value("Customer",doc_name,"website_userid",user_id)
#     frappe.db.commit()
#     frappe.sendmail(
#     recipients=frappe.db.get_value("Customer",doc_name,"email_id"),
#     subject="Your Login Details",
#     message="Dear {},<br/>Your account has been setup,below is your login details<br/>ID : <b>{}</b><br/>Password : <b>{}</b>".format(frappe.db.get_value("Customer",doc_name,"customer_name"),frappe.db.get_value("Customer",doc_name,"email_id"),password))
#     customer_doc=frappe.get_doc("Customer",doc_name,"name")
#     customer_doc.flags.ignore_permissions = True
#     customer_doc.save()

# @frappe.whitelist()
# def get_wordpress_url():
#     return cstr(frappe.get_value("Booking Settings",None,"customer_api"))

@frappe.whitelist()
def create_customer_wordpress(self):
    
    if Customer_API_URL_LIVE:
        random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(8)])
        # frappe.msgprint(random_string)

        data_object = {
        "erp_user_id": cstr(self.name),
        "username": cstr(self.customer_name), 
        "email": cstr(self.email_id),
        "password":random_string,
        "mobile":cstr(self.mobile_no)
        }

        headers_content = {
        'Content-Type': 'application/json',
        }
        response_data = requests.post(Customer_API_URL_LIVE,headers=headers_content,data=json.dumps(data_object))
        # frappe.msgprint(cstr(response_data.json()))
        if cstr(response_data.json()['status']) == "404":
            frappe.msgprint("Customer <b>{}</b> is already created in website".format(cstr(self.name)))
            
        elif cstr(response_data.json()['status']) == "200":
            frappe.msgprint("Customer <b>{}</b> has been successfully created in website".format(cstr(self.name)))
            
            self.website_userid = response_data.json()['user_id']
            self.customer_password = random_string
            frappe.sendmail(
            recipients=cstr(self.email_id),
            subject="Your Login Details",
            message="Dear {},<br/>Your account has been setup,below is your login details<br/>ID : <b>{}</b><br/>Password : <b>{}</b>".format(cstr(self.customer_name),cstr(self.email_id),random_string))

    
    
    

