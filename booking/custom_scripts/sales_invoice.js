frappe.ui.form.on('Sales Invoice', {
	refresh: function(frm) {
		
	},
	onload: function(frm, cdt, cdn) {
		if(frm.doc.__islocal && frm.doc.is_pos == 1)
		{
			if(frm.doc.selling_price_list)
			{

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
			        	var item = frm.doc.items || [];
			        	for(var i=0;i<item.length;i++) {
			        		if(item[i].item_code == frm.doc.items[0]["item_code"])
			        		{
			        			item[i].price_list_rate = data.message.price_list_rate
			        			item[i].rate = data.message.price_list_rate
			        		}
						}
						// console.log(data.message.price_list_rate);
			            // frappe.model.set_value(cdt, cdn, "price_list_rate", data.message.price_list_rate); //might need to be data.message[0]
			            refresh_field("items");
			        }
			    })
			}
		}
	},
	'onload_post_render': function(frm) {
		// console.log(frm.doc.selling_price_list)
	}	
});


