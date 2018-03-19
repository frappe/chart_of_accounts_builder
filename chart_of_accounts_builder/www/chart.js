frappe.ready(function() {
	frappe.require("/assets/frappe/js/lib/awesomplete/awesomplete.min.js");
	frappe.require("/assets/frappe/js/lib/awesomplete/awesomplete.css");
	frappe.require("/assets/js/dialog.min.js");
	frappe.require("/assets/frappe/js/lib/jquery/jquery.hotkeys.js");

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
						me.add_child();
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
			if( !cint(frappe.utils.get_url_arg("forked")) || cint(frappe.utils.get_url_arg("submitted")) ) {
				this.fork_charts();
			}

			if ( cint(frappe.utils.get_url_arg("forked")) && !cint(frappe.utils.get_url_arg("submitted")) ) {
				this.bind_node_toolbar();
				this.add_root();
				this.submit_charts();
			}

			if ( cint(frappe.utils.get_url_arg("forked")) && cint(frappe.utils.get_url_arg("submitted")) ) {
				this.download_chart();
			}

			this.add_star();
		},

		bind_node_toolbar: function() {
			var me = this;

			$(".tree-link").each(function($link) {
				var data_account_name = $(this).attr('data-account-name');
				var $toolbar_wrapper = $('.tree-node-toolbar-wrapper[data-account-name="'+data_account_name+'"]');
				if($toolbar_wrapper.find('.tree-node-toolbar').length > 0) return;

				var $toolbar = $('<span class="tree-node-toolbar btn-group" ' +
					'data-account-name="'+ data_account_name +'"></span>').appendTo($toolbar_wrapper).hide();
				$.each(me.toolbar, function(i, item) {
					var link = $("<button class='btn btn-default btn-xs hidden-xs'></button>")
						.html(item.label)
						.appendTo($toolbar)
						.click(function() {
							item.click(me, this);
							return false;
						}
					);
				})

			}).on("click", function() {
				var data_account_name = $(this).attr('data-account-name');
				var $toolbar = $('.tree-node-toolbar[data-account-name="'+data_account_name+'"]');
				me.selected_node = this;
				me.current_toolbar = $toolbar;

				$('.bold').removeClass('bold');
				$(this).addClass("bold");

				$('.tree-node-toolbar').hide();
				me.current_toolbar.show();
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

			//show root_type if root and tax_rate if account_type is tax
			var fd = d.fields_dict;

			var is_root = node.attr("data-parent-account")=="None" ? true : false;
			$(fd.root_type.wrapper).toggle(is_root);
			$(fd.is_group.wrapper).toggle(!is_root);
			$(fd.account_type.wrapper).toggle(!is_root);

			$(fd.tax_rate.wrapper).toggle(fd.account_type.get_value()==='Tax');

			$(fd.account_type.input).change(function() {
				$(fd.tax_rate.wrapper).toggle(fd.account_type.get_value()==='Tax');
			})

			// make account name field non-editable
			var field = d.get_field("account_name");
			field.df.read_only = 1;
			field.refresh();

			d.set_primary_action(__("Submit"), function() {
				var btn = this;
				var v = d.get_values();
				if(!v) return;
				v.name = node.attr("data-name")
				v.is_root = is_root

				return frappe.call({
					args: v,
					method: 'chart_of_accounts_builder.utils.update_account',
					freeze: true,
					callback: function(r) {
						d.hide();
						window.location.reload();
					}
				});
			});

			d.show();
		},

		add_child: function() {
			var node = $(this.selected_node);

			if(!(node && cint(node.attr("data-is-group")))) {
				frappe.msgprint(__("Select a group node first."));
				return;
			}

			this.make_new_account(node.attr('data-name'), node.attr('data-company'))
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
						"new": v.new_account_name,
						"ignore_permissions": true
					},
					freeze: true,
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
				method: 'chart_of_accounts_builder.utils.delete_account',
				args: {
					account: node.attr("data-name")
				},
				freeze: true,
				callback: function(r, rt) {
					if(!r.exc) {
						window.location.reload();
					}
				}
			})
		},

		make_new_account: function(parent_account, company) {
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
					{ fieldtype:'Data', fieldname:'tax_rate', label:__('Tax Rate') },
					{
						fieldtype:'Select', fieldname:'root_type', label:__('Root Type'),
						options: ['Asset', 'Liability', 'Equity', 'Income', 'Expense'].join('\n')
					},
				]
			})

			var fd = d.fields_dict;

			//show tax rate if account type is tax
			$(fd.tax_rate.wrapper).toggle(false);
			$(fd.account_type.input).change(function() {
				$(fd.tax_rate.wrapper).toggle(fd.account_type.get_value()==='Tax');
			})

			// In case of root, show root type and hide account_type, is_group
			var is_root = parent_account==null ? true : false;
			$(fd.is_group.wrapper).toggle(!is_root);
			$(fd.account_type.wrapper).toggle(!is_root);
			$(fd.root_type.wrapper).toggle(is_root);

			// bind primary action
			d.set_primary_action(__("Create"), function() {
				var btn = this;
				var v = d.get_values();
				if(!v) return;

				v.parent_account = parent_account;
				v.company = company;
				v.is_root = is_root ? 1 : 0;
				v.is_group = is_root ? 1 : v.is_group;
				v.ignore_permissions = 0;

				return frappe.call({
					args: v,
					method: 'erpnext.accounts.utils.add_ac',
					freeze: true,
					callback: function(r) {
						d.hide();
						window.location.reload();
					}
				});
			});

			d.show()
		},

		add_root: function() {
			var me = this;
			var company = frappe.utils.get_url_arg("company");
			$(".add-root-button").on("click", function() {
				me.make_new_account(null, company);
			})
		},

		fork_charts: function() {
			var company = frappe.utils.get_url_arg("company");
			$(".fork-button").addClass("btn-primary").on("click", function() {
				return frappe.call({
					method: 'chart_of_accounts_builder.utils.fork',
					args: {
						company: company
					},
					freeze: true,
					callback: function(r, rt) {
						if(!r.exc && r.message) {
							window.location.href = "/chart?company=" + r.message + "&forked=1&submitted=0"
						}
					}
				})
			})
		},

		submit_charts: function() {
			var company = frappe.utils.get_url_arg("company");
			$(".submit-chart").on("click", function() {
				return frappe.call({
					method: 'chart_of_accounts_builder.utils.submit_chart',
					args: {
						company: company
					},
					freeze: true,
					callback: function(r, rt) {
						if(!r.exc) {
							window.location.href = "/all_charts"
						}
					}
				})
			})
		},

		add_star: function() {
			var company = frappe.utils.get_url_arg("company");
			$(".star-button").on("click", function() {
				return frappe.call({
					method: 'chart_of_accounts_builder.utils.add_star',
					args: {
						company: company
					},
					freeze: true,
					callback: function(r, rt) {
						if(!r.exc && r.message) {
							$(".star-count").html(r.message);
						}
					}
				})
			})
		},

		download_chart: function() {
			var company = frappe.utils.get_url_arg("company");
			$(".download-chart").on("click", function() {
				return frappe.call({
					method: "chart_of_accounts_builder.utils.export_submitted_coa",
					args: {
						chart: company
					},
					callback: function() {
						var file_url = "/files/submitted_charts/" + company + ".tar.gz"
						window.open(file_url);
					}
				})
			});
		}
	}),

	erpnext.coa = new erpnext.ChartBuilder();
	erpnext.coa.bind_events();
});
