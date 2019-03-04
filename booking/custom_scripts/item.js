
// _f.Frm.prototype.savetrash = function(frm,doc) {
	
//      this.validate_form_action("Delete");
//      frappe.model.delete_doc(this.doctype, this.docname, function(r) {
//         window.history.back();
// 	});
//      delete_item(this.doctype, this.docname)

// };

cur_frm.add_fetch('item_group','is_activity','is_service')
cur_frm.add_fetch('item_group','is_product_group','is_product')

frappe.ui.form.on('Item', {
	refresh: function(frm) {
		// create_item_in_website(frm.doc)
		//frm.refresh_field("items");
		//frm.reload_doc()
		console.log("refresh")
	}

});

cur_frm.cscript.validate= function(doc,dt,dn){
	//create_item_in_website(doc)
}



cur_frm.cscript.website_product_id= function(frm,dt,dn){

	refresh_field("items");
	refresh_field("website_product_id");
}	

var create_item_in_website = function(doc){
	
	// Create product on website 
	if(doc.show_in_website == 1)
	{
		$.ajax({
		    url: 'http://antoniosbarber.offtomalta.com/wp-json/antonio/api/product',
		    dataType: 'json',
		    method: 'post',
		    contentType: 'application/json',
		    data: JSON.stringify({ 
		    	"product_title": doc.item_name, 
		    	"product_sku": doc.item_code,
				"price":doc.valuation_rate
			}),
		    processData: false,
		    success: function( data, textStatus, jQxhr ){
		    	if(data["product_id"])

		    	{	
		    		console.log(data)
	  
		       		cur_frm.set_value('website_product_id', data["product_id"]);
					cur_frm.refresh();
					refresh_field("website_product_id");
				}				
			 	
		    },
		    error: function( jqXhr, textStatus, errorThrown ){
		        console.log( errorThrown );
		    }
		});
	}
}

cur_frm.fields_dict['service_provider'].grid.get_field('provider').get_query = function(doc) {
	return {
		 filters: { 'is_service_provider': 1 }
	}
}


var delete_item = function(doctype,docname){
		$.ajax({
	    url: 'http://antoniosbarber.offtomalta.com/wp-json/antonio/api/product',
	    dataType: 'json',
	    method: 'post',
	    contentType: 'application/json',
	    data: JSON.stringify({ 
	    	"product_sku": [docname],
			"delete_product":"yes"
		}),
	    processData: false,
	    success: function( data, textStatus, jQxhr ){
	    	if(data.status == 200){
			console.log(data);
			frappe.show_alert({message: __("Deleted"), indicator: 'red'});
			}
	    },
	    error: function( jqXhr, textStatus, errorThrown ){
	        console.log( errorThrown );
	    }
	});
}

frappe.ui.form.on("Item", "all_staff_provide", function(doc)
{  

console.log(doc.all_staff_provide)	

	console.log("hi")

frappe.call({

	method : 'get_all_employee',
	doc:doc,
	args:{},
	callback: (r) => {
		console.log(r.message)

		


		// console.log(r.message[0]['name'])
		// var newrow = frappe.model.add_child(doc, "Service Provider", "provider");
		// newrow.provider = r.message[0]['name'];
		// newrow.provider_name = r.message[0]['employee_name']
		// newrow.
		// refresh_field("provider");
	}
})

});

