Customer_url = ''



frappe.ui.form.on('Customer', {
	refresh: function(frm) {

	},
	onload: function(frm) {

	frappe.call({
	method : 'booking.booking.customer.get_wordpress_url',
	args:{},
	callback: (r) => {
		Customer_url = r.message
		}
	})

	}
});

function makepass() {
  var text = "";
  var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

  for (var i = 0; i < 8; i++)
    text += possible.charAt(Math.floor(Math.random() * possible.length));

  return text;
}




cur_frm.cscript.make_customer = function(doc,dt,dn){
		var pass = makepass()
		console.log(pass)
		$.ajax({
		    url: Customer_url,
		    dataType: 'json',
		    type: 'post',
		    contentType: 'application/json',
		    data: JSON.stringify({
		    	"erp_user_id": doc.name,
		    	"username": doc.customer_name, 
		    	"email": doc.email_id,
		    	"password":pass,
		    	"mobile":doc.mobile_no
		    }),
		    processData: false,
		    success: function( data, textStatus, jQxhr ){
		        console.log(data)
		        if (data.message != "email already exist"){
		           frappe.call({
		     					method: "booking.booking.customer.save_customer_password",
		     					args: {
		     						doc_name:doc.name,
		     						password:pass,
		     						user_id:data.user_id
		     					},
		     			callback: function(r) {
		     				
		     			}
		     				})
		       }
		    },
		    error: function( jqXhr, textStatus, errorThrown ){
		        console.log( errorThrown );
		    }
		});

			
}


