frappe.ui.form.on('Sales Invoice', {
	refresh: function(frm) {
		
	},
	onload: function(frm, cdt, cdn) {
		
		console.log(frm.doc.__islocal)
		console.log(frm.doc.is_pos)
		if(frm.doc.__islocal && frm.doc.is_pos == 1)
		{
			console.log("hello")
			if(frm.doc.selling_price_list)
			{
				console.log("hello1")
				console.log(frm.doc.items[0]["item_code"])
				console.log(frm.doc.selling_price_list)
				frappe.call({
			        method: "frappe.client.get_value",
			        args: {
			            doctype: "Item Price",
			            fieldname: "price_list_rate",
			            filters: {
			            "item_code": frm.doc.items[0]["item_code"],
			            "price_list": frm.doc.selling_price_list
			            }
			        },
			        callback: function (data) {
						console.log(data.message);
			            frappe.model.set_value(cdt, cdn, "price_list_rate", data.message); //might need to be data.message[0]
			        }
			    })
			}
		}
	},
	'onload_post_render': function(frm) {
		console.log(frm.doc.selling_price_list)
	}	
});


