Customer_url = ''
Customer_create_flag = 0


frappe.ui.form.on('Customer', {
	refresh: function(frm) {
	},
	onload: function(frm) {

	

	}
	// 	,
	// validate: function(frm){

	// 	make_user_on_website(doc,dt,dn)
	// }
});


function makepass() {
  var text = "";
  var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

  for (var i = 0; i < 8; i++)
    text += possible.charAt(Math.floor(Math.random() * possible.length));

  return text;
}


function get_customer_api(){
	frappe.call({
	method : 'booking.booking.customer.get_wordpress_url',
	args:{},
	callback: (r) => {
				// console.log(r)
				
				Customer_url = r.message
				// console.log(Customer_url)
				if(!Customer_url){
					// console.log("in condition")
					Customer_create_flag = 0
				}
				else{
					// console.log("else")

					Customer_create_flag = 1
				}
		}
	})
}

cur_frm.cscript.customer_mobile_number_ = function(doc,dt,dn){

if (doc.customer_mobile_number_){
	cur_frm.set_value("mobile_no", doc.customer_mobile_number_)
}
}
cur_frm.cscript.customer_email_id = function(doc,dt,dn){

if (doc.customer_email_id){
	cur_frm.set_value("email_id", doc.customer_email_id)
}
}
// function make_user_on_website(doc,dt,dn){
// 	var name = doc.name
// 	var customer = doc.customer_name
// 	var email = doc.email_id
// 	var mobile = doc.mobile_no
// 	frappe.call({
// 	method : 'booking.booking.customer.create_customer_wordpress',
// 	args:{name,customer,email,mobile},
// 	callback: (r) => {
// 				// console.log(r)
				
// 				Customer_url = r.message
// 				// console.log(Customer_url)
// 				if(!Customer_url){
// 					// console.log("in condition")
// 					Customer_create_flag = 0
// 				}
// 				else{
// 					// console.log("else")

// 					Customer_create_flag = 1
// 				}
// 		}
// 	})
// 		// get_customer_api()
// 		// var pass = makepass()
// 		// // console.log(pass)
// 		// // console.log(Customer_create_flag)
// 		// if(Customer_create_flag == 1)
// 		// {
// 		// 	$.ajax({
// 		// 		    url: Customer_url,
// 		// 		    dataType: 'json',
// 		// 		    type: 'post',
// 		// 		    contentType: 'application/json',
// 		// 		    data: JSON.stringify({
// 		// 		    	"erp_user_id": doc.name,
// 		// 		    	"username": doc.customer_name, 
// 		// 		    	"email": doc.email_id,
// 		// 		    	"password":pass,
// 		// 		    	"mobile":doc.mobile_no
// 		// 		    }),
// 		// 		    processData: false,
// 		// 		    success: function( data, textStatus, jQxhr ){
// 		// 		        // console.log(data)
// 		// 		        if (data.message != "email already exist"){
// 		// 		           frappe.call({
// 		// 		     					method: "booking.booking.customer.save_customer_password",
// 		// 		     					args: {
// 		// 		     						doc_name:doc.name,
// 		// 		     						password:pass,
// 		// 		     						user_id:data.user_id
// 		// 		     					},
// 		// 		     			callback: function(r) {
				     				
// 		// 		     			}
// 		// 		     				})
// 		// 		       }
// 		// 		    },
// 		// 		    error: function( jqXhr, textStatus, errorThrown ){
// 		// 		        console.log( errorThrown );
// 		// 		    }
// 		// 		});
// 		// }
// 		// else{
// 		// 	// console.log("Customer Api not found")
// 		// }

			
// }


