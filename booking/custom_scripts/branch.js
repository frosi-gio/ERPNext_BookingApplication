 /*---------------------------------------------------------------------------
 company wise warehouse filter
 --------------------------------------------------------------------------- */
cur_frm.fields_dict.warehouse.get_query = function(doc, cdt, cdn) {
	return{
		filters: {
			'company': doc.company
		}
	}
}

 /*---------------------------------------------------------------------------
 company wise cost center filter
 --------------------------------------------------------------------------- */
cur_frm.fields_dict.cost_center.get_query = function(doc, cdt, cdn) {
	return{
		filters: {
			'company': doc.company
		}
	}
}

