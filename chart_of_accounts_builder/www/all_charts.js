erpnext = {};
erpnext.all_charts = {};

frappe.ready(function() {
	frappe.require("/assets/frappe/js/lib/awesomplete/awesomplete.min.js");
	frappe.require("/assets/frappe/js/lib/awesomplete/awesomplete.css");
	frappe.require("/assets/js/dialog.min.js");

	frappe.require("/assets/js/control.min.js");
	
	erpnext.all_charts.make_new_chart();

	// hide all charts by default
	if(frappe.session.user!="Guest") {
		$(".tab1").hide();
	}

	// toggle all charts
	$('.show_all_charts').change(function() {
		if($('[data-fieldname="show_all_charts"]')[0].checked) {
			$(".tab2").hide();
			$(".tab1").show();
		} else {
			$(".tab2").show();
			$(".tab1").hide();
		}
	})
});


erpnext.all_charts.make_new_chart = function() {
	$(".new-chart").on("click", function() {
		frappe.call({
			method: "chart_of_accounts_builder.utils.get_countries",
			callback: function(r) {
				if(!r.exc) {
					var d = new frappe.ui.Dialog({
						title:__('New Chart'),
						fields: [
							{
								fieldtype:'Select', fieldname:'country',
								label:__('Country'), reqd:true,
								options: [""].concat(r.message).join("\n")
							}
						]
					});

					d.set_primary_action(__("Create"), function() {
						var btn = this;
						var v = d.get_values();
						if(!v) return;

						return frappe.call({
							method:"chart_of_accounts_builder.utils.create_new_chart",
							args: {
								"country": v.country
							},
							freeze: true,
							btn: d.get_primary_btn(),
							callback: function(r,rt) {
								if(!r.exc && r.message) {
									d.hide();
									window.location.href = "/chart?company=" + r.message + "&forked=1&submitted=0"
								}
							}
						});
					});

					d.show()
				}
			}
		})
	})
}
