// Copyright (c) 2018, August Infotech and contributors
// For license information, please see license.txt

frappe.ui.form.on('Booking Settings', {
    refresh: function(frm) {

    }
});

// cur_frm.cscript.allow_google_calendar_access= function(doc,dt,dn){
// 		frappe.call({
// 			method: "booking.booking.event.google_callback",
// 			args: {},
// 			callback: function(r) {
// 				if (r.message){
// 					window.open(r.message.url);
// 				}
// 			}
// 		})
// }