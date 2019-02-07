# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime, timedelta
from frappe.utils import flt, cint, cstr, add_days, getdate
from frappe.model.naming import make_autoname
import json
from frappe import _
import frappe.defaults
import frappe.desk.reportview

def validate(doc, method):
	pass

def after_insert(doc, method):

	default_pos_user_role = frappe.db.get_value("Booking Settings", None, "default_pos_user_role")

	# ---------------------------------------------------------------------------
	# get all users having the role of system manager
	# --------------------------------------------------------------------------- */
	system_user_list = frappe.desk.reportview.execute("User", filters = [["Has Role","role","=",cstr(default_pos_user_role)]],
			fields = ["name"],
			limit_start=0, limit_page_length=0, order_by = "name", as_list=True)

	# ---------------------------------------------------------------------------
	# get all mode of payment
	# --------------------------------------------------------------------------- */
	mode_of_payment_list = frappe.get_all('Mode of Payment', filters={}, fields=['name'])
	default_pos_mode_of_payment = frappe.db.get_value("Booking Settings", None, "default_pos_mode_of_payment")
	
	pos_profile = frappe.get_doc("POS Profile", doc.name)

	# ---------------------------------------------------------------------------
	# set applicable users in pos profile child table (applicable_for_users)
	# --------------------------------------------------------------------------- */
	if not len(pos_profile.applicable_for_users):
		for user in system_user_list:
			pos_profile.append("applicable_for_users",{
				"user": str(user[0])
				})

	# ---------------------------------------------------------------------------
	# set mode of payments in pos profile child table (payments)
	# --------------------------------------------------------------------------- */
	# for mop in mode_of_payment_list:
	# 	pos_profile.append("payments",{
	# 		"default": 1 if cstr(mop.name) == cstr(default_pos_mode_of_payment) else 0,
	# 		"mode_of_payment": cstr(mop.name),
	# 		"type": cstr(frappe.db.get_value("Mode of Payment", cstr(mop.name), "type"))
	# 		})

	pos_profile.flags.ignore_permissions = True
	pos_profile.save()	