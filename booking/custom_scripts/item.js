// _f.Frm.prototype.savetrash = function(frm,doc) {

//      this.validate_form_action("Delete");
//      frappe.model.delete_doc(this.doctype, this.docname, function(r) {
//         window.history.back();
// 	});
//      delete_item(this.doctype, this.docname)

// };

// cur_frm.add_fetch('item_group','is_activity','is_service')
// cur_frm.add_fetch('item_group','is_product_group','is_product')


// frappe.ui.form.on('Item', {
// 	refresh: function(frm) {
// 		// create_item_in_website(frm.doc)
// 		//frm.refresh_field("items");
// 		//frm.reload_doc()
// 		// console.log("refresh")
// 	},
// 	onload: function(frm) {
// 		if(!frm.doc.__islocal)
// 		{
// 			cur_frm.set_df_property("all_staff_provide", "read_only",1)
// 			cur_frm.set_df_property("service_provider", "read_only",1)
// 			var provider = frappe.meta.get_docfield("Service Provider","provider", cur_frm.doc.name)
// 			provider.read_only = 1
// 			var billing_rate = frappe.meta.get_docfield("Service Provider","billing_rate", cur_frm.doc.name)
// 			billing_rate.read_only = 1
// 		}
// 	}

// });

// cur_frm.cscript.validate= function(doc,dt,dn){
// 	//create_item_in_website(doc)
// }



// cur_frm.cscript.website_product_id= function(frm,dt,dn){

// 	refresh_field("items");
// 	refresh_field("website_product_id");
// }	

// var create_item_in_website = function(doc){

// 	// Create product on website 
// 	if(doc.show_in_website == 1)
// 	{
// 		$.ajax({
// 		    url: 'http://antoniosbarber.offtomalta.com/wp-json/antonio/api/product',
// 		    dataType: 'json',
// 		    method: 'post',
// 		    contentType: 'application/json',
// 		    data: JSON.stringify({ 
// 		    	"product_title": doc.item_name, 
// 		    	"product_sku": doc.item_code,
// 				"price":doc.valuation_rate
// 			}),
// 		    processData: false,
// 		    success: function( data, textStatus, jQxhr ){
// 		    	if(data["product_id"])

// 		    	{	
// 		       		cur_frm.set_value('website_product_id', data["product_id"]);
// 					cur_frm.refresh();
// 					refresh_field("website_product_id");
// 				}				

// 		    },
// 		    error: function( jqXhr, textStatus, errorThrown ){
// 		        console.log( errorThrown );
// 		    }
// 		});
// 	}
// }

// cur_frm.fields_dict['service_provider'].grid.get_field('provider').get_query = function(doc) {
// 	return {
// 		 filters: { 'is_service_provider': 1 }
// 	}
// }


// var delete_item = function(doctype,docname){
// 		$.ajax({
// 	    url: 'http://antoniosbarber.offtomalta.com/wp-json/antonio/api/product',
// 	    dataType: 'json',
// 	    method: 'post',
// 	    contentType: 'application/json',
// 	    data: JSON.stringify({ 
// 	    	"product_sku": [docname],
// 			"delete_product":"yes"
// 		}),
// 	    processData: false,
// 	    success: function( data, textStatus, jQxhr ){
// 	    	if(data.status == 200){
// 			frappe.show_alert({message: __("Deleted"), indicator: 'red'});
// 			}
// 	    },
// 	    error: function( jqXhr, textStatus, errorThrown ){
// 	        console.log( errorThrown );
// 	    }
// 	});
// }

// cur_frm.cscript.all_staff_provide = function(doc,dt,dn)
// {  
// 	if(doc.all_staff_provide)
// 	{
// 		frappe.call({
// 			method: "booking.booking.item.get_all_employee",
// 			args: {},
// 			callback: function(r) {
// 				for(var item in r.message)
// 				{
// 					var newrow = frappe.model.add_child(doc, "Service Provider", "service_provider");
// 					newrow.provider = r.message[item]['name'];
// 					newrow.provider_name = r.message[item]['employee_name'];
// 					newrow.billing_rate = doc.standard_rate;
// 					refresh_field("service_provider");
// 				}
// 			}
// 		})
// 	}

// }