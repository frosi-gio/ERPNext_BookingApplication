/* ---------------------------------------------------------------------------
/ Doc events
/ --------------------------------------------------------------------------- */ 

frappe.ui.form.on('Employee', {
	refresh: function(frm,dt,dn) {	
		
	}
	
});

cur_frm.cscript.all_services = function(doc, cdt, cdn) {
	// frappe.msgprint("Hello")
}

/* ---------------------------------------------------------------------------
/ services change event
/ --------------------------------------------------------------------------- */ 
cur_frm.cscript.services = function(doc, cdt, cdn) {
	var is_call = 1
	if(locals[cdt][cdn]['services'])
	{
		var child_table = cur_frm.doc.services_type || [];
		var count = 0
		var exist_in_row = ''
		for(var i = 0; i < child_table.length; i++)
		{
			if(child_table[i].services == locals[cdt][cdn]['services'])
			{
				count+=1
				if(!exist_in_row)
				{
					exist_in_row = count
				}
				 
				if (count > 1)
				{
					// check for duplicate service name and remove if exist.
					var service_name = child_table[i].services.toString();
					cur_frm.get_field("services_type").grid.grid_rows[i].remove();
					cur_frm.refresh();
					is_call = 0
					frappe.msgprint("You can't select duplicate service. <b>" + service_name + "</b> has already exist in row <b>" + exist_in_row.toString() + ".</b>");
				}
			}
		}
		if(is_call)
		{
			// get services by it's group.
			get_service(doc,cdt,cdn,locals[cdt][cdn]['services']);
		}
	}
	
}

frappe.ui.form.on("Services Type", "services_type_add", function(doc,cdt,cdn) {
	//cur_frm.cscript.services
});

frappe.ui.form.on("Services Type", "services_type_remove", function(doc,cdt,cdn) {
	console.log(doc.service_type)
	//cur_frm.cscript.services
});

 
/* ---------------------------------------------------------------------------
/ Funcrion: get services
/ --------------------------------------------------------------------------- */ 
var get_service = function(doc,cdt,cdn,service_name){
	if(service_name)
	{
		frappe.call({
			method: "booking.booking.employee.get_service_list",
			args: { item_group: service_name },
			callback: function(r) {
				for(var item in r.message)
				{
					var newrow = frappe.model.add_child(doc, "Services", "services");
					newrow.service = r.message[item]['name'];
					newrow.billing_rate = 0 ;
					refresh_field("services");
				}
			}
		})
	}
}

/*function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}*/
