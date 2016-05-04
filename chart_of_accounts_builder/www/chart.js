frappe.provide("erpnext.ChartBuilder");

erpnext.ChartBuilder = Class.extend({
	init: function() {
		var me = this;
		this.toolbar = [
			{
				label: __("Edit"),
				click: function(node) {
					me.edit_account();
				},
			},
			{
				label: __("Add Child"),
				click: function() {
					me.make_new()
				},
			},
			{
				label: __("Rename"),
				click: function(node) {
					me.rename_account();
				},
			},
			{
				label: __("Delete"),
				click: function(node) {
					me.delete_account();
				},
			}
		]
	},

	bind_events: function() {		
		if(cint(get_url_arg("submitted"))) return;

		if(!cint(get_url_arg("forked"))) {
			this.fork_charts();
		} else {
			this.bind_node_toolbar();
			this.submit_charts();
		}
	},

	bind_node_toolbar: function() {
		var me = this;

		$(".tree-link").on("click", function() {
			me.selected_node = this;

			$('.bold').removeClass('bold');
			$(this).addClass("bold");

			var toolbar = $('<span class="tree-node-toolbar btn-group"></span>').insertAfter(this);

			$.each(me.toolbar, function(i, item) {
				var link = $("<button class='btn btn-default btn-xs'></button>")
					.html(item.label)
					.appendTo(toolbar)
					.click(function() {
						item.click(me, this);
						return false;
					}
				);

				link.addClass("hidden-xs");

			})

			if(me.current_toolbar) {
				$(me.current_toolbar).toggle(false);
			}
			me.current_toolbar = toolbar;
			$(this).toggle(true);

		});
	},

	edit_account: function() {
		var node = $(this.selected_node);

		var d = new frappe.ui.Dialog({
			title: __('Edit Properties'),
			fields: [
				{
					fieldtype: "Data", fieldname: "account_name", label: "Account Name",
					"default": node.attr("data-account-name")
				},
				{
					fieldtype:'Check', fieldname:'is_group', label:__('Is Group'),
					default: cint(node.attr("data-is-group")),
					description: __('Further accounts can be made under Groups, but entries can be made against non-Groups')},
				{
					fieldtype:'Select', fieldname:'account_type', label:__('Account Type'),
					options: ['', 'Bank', 'Cash', 'Receivable', 'Payable', 'Stock', 'Tax', 
						'Chargeable', 'Cost of Goods Sold', 'Stock Received But Not Billed', 
						'Expenses Included In Valuation', 'Stock Adjustment', 'Fixed Asset', 
						'Depreciation', 'Accumulated Depreciation', 'Round Off', 'Temporary'].join('\n'),
					default: node.attr("data-account-type"),
					description: __("Optional. This setting will be used to filter in various transactions.")},
				{
					fieldtype:'Select', fieldname:'root_type', label:__('Root Type'),
					options: ['Asset', 'Liability', 'Equity', 'Income', 'Expense'].join('\n'),
					default: node.attr("data-root-type")
				},
				{ 
					fieldtype:'Data', fieldname:'tax_rate', label:__('Tax Rate'), 
					default: node.attr("data-tax-rate")
				}
			]
		})

		d.set_primary_action(__("Submit"), function() {
			var btn = this;
			var v = d.get_values();
			if(!v) return;
			v.name = node.attr("data-name")

			return frappe.call({
				args: v,
				method: 'chart_of_accounts_builder.utils.update_account',
				callback: function(r) {
					d.hide();
					window.location.reload();
				}
			});
		});
		
		//show root_type if root and tax_rate if account_type is tax
		var fd = d.fields_dict;
		
		$(fd.root_type.wrapper).toggle(node.attr("data-parent-account")=="None");
		$(fd.tax_rate.wrapper).toggle(fd.account_type.get_value()==='Tax');
		
		$(fd.account_type.input).change(function() {
			$(fd.tax_rate.wrapper).toggle(fd.account_type.get_value()==='Tax');
		})

		// make account name field non-editable
		var field = d.get_field("account_name");
		field.df.read_only = 1;
		field.refresh();

		d.show();
	},

	make_new: function() {
		var node = $(this.selected_node);

		if(!(node && cint(node.attr("data-is-group")))) {
			frappe.msgprint(__("Select a group node first."));
			return;
		}

		var d = new frappe.ui.Dialog({
			title:__('New Account'),
			fields: [
				{
					fieldtype:'Data', fieldname:'account_name', label:__('New Account Name'), reqd:true,
					description: __("Name of new Account. Note: Please don't create accounts for Customers and Suppliers")},
				{
					fieldtype:'Check', fieldname:'is_group', label:__('Is Group'),
					description: __('Further accounts can be made under Groups, but entries can be made against non-Groups')},
				{
					fieldtype:'Select', fieldname:'account_type', label:__('Account Type'),
					options: ['', 'Bank', 'Cash', 'Receivable', 'Payable', 'Stock', 'Tax', 
						'Chargeable', 'Cost of Goods Sold', 'Stock Received But Not Billed', 
						'Expenses Included In Valuation', 'Stock Adjustment', 'Fixed Asset', 
						'Depreciation', 'Accumulated Depreciation', 'Round Off', 'Temporary'].join('\n'),
					description: __("Optional. This setting will be used to filter in various transactions.")},
				{ fieldtype:'Data', fieldname:'tax_rate', label:__('Tax Rate') }
			]
		})
		
		//show tax rate if account type is tax
		var fd = d.fields_dict;	
		$(fd.tax_rate.wrapper).toggle(false);
		$(fd.account_type.input).change(function() {
			$(fd.tax_rate.wrapper).toggle(fd.account_type.get_value()==='Tax');
		})

		// bind primary action
		d.set_primary_action(__("Create"), function() {
			var btn = this;
			var v = d.get_values();
			if(!v) return;

			v.parent_account = node.attr('data-name');
			v.company = node.attr('data-company');

			return frappe.call({
				args: v,
				method: 'erpnext.accounts.utils.add_ac',
				callback: function(r) {
					d.hide();
					window.location.reload();
				}
			});
		});

		d.show()
	},

	rename_account: function() {
		var selected_account_id = $(this.selected_node).attr("data-name");
		var selected_account_name = $(this.selected_node).attr("data-account-name");

		var d = new frappe.ui.Dialog({
			title:__('Rename Account'),
			fields: [
				{fieldtype:'Data', fieldname:'new_account_name',
				label:__('New Account Name'), reqd:true, default: selected_account_name}
			]
		});

		d.set_primary_action(__("Rename"), function() {
			var btn = this;
			var v = d.get_values();
			if(!v) return;

			return frappe.call({
				method:"frappe.model.rename_doc.rename_doc",
				args: {
					doctype: "Account",
					old: selected_account_id,
					"new": v.new_account_name
				},
				btn: d.get_primary_btn(),
				callback: function(r,rt) {
					if(!r.exc) {
						d.hide();
						window.location.reload();
					}
				}
			});
		});

		d.show()
	},

	delete_account: function() {
		var node = $(this.selected_node);

		return frappe.call({
			method: 'frappe.client.delete',
			args: {
				doctype: "Account",
				name: node.attr("data-name")
			},
			callback: function(r, rt) {
				if(!r.exc) {
					window.location.reload();
				}
			}
		})
	},
	
	fork_charts: function() {
		var company = get_url_arg("company");
		$(".fork-button").addClass("btn-primary").on("click", function() {
			return frappe.call({
				method: 'chart_of_accounts_builder.utils.fork',
				args: {
					company: company
				},
				callback: function(r, rt) {
					if(!r.exc && r.message) {
						window.location.href = "/chart?company=" + r.message + "&forked=1&submitted=0"
					}
				}
			})
		})
	},
	
	submit_charts: function() {
		var company = get_url_arg("company");
		$(".submit-chart").on("click", function() {
			return frappe.call({
				method: 'chart_of_accounts_builder.utils.submit_chart',
				args: {
					company: company
				},
				callback: function(r, rt) {
					if(!r.exc) {
						window.location.href = "/all_charts"
					}
				}
			})
		})
	}
})


frappe.ready(function() {
	frappe.require("/assets/js/dialog.min.js");
	erpnext.coa = new erpnext.ChartBuilder();
	erpnext.coa.bind_events();
});
