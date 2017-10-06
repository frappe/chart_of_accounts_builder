<h1 class="page-title">Chart of Accounts Builder Help</h1>
<h3 class="page-sub-title">Portal to help the ERPNext / Frappe community contribute chart of accounts.</h3>

**Source:**
[https://github.com/frappe/chart_of_accounts_builder](https://github.com/frappe/chart_of_accounts_builder)

### 1. How to use

1. Login (or sign up and login).
1. Select any existing chart to fork it and start editing.
1. Add, edit, delete, rename accounts and set account / root types.
1. Or create your own chart from scratch.
1. For help, comments or report a bug, <a href="https://github.com/frappe/chart_of_accounts_builder/issues" target="_blank">please use GitHub Issues</a>.


### 2. What to do with existing charts

Most of the standard charts are bootstraped from Odoo repository and are unveried. There are many things to do with those charts.

1. Add any missing account
1. Delete any wrong/unwanted account
1. Rename any existing account
1. Identify an account is a group or ledger
1. Set Root Type for root accounts. Root Type must be one of the Asset, Liabiity, Expense, Income and Equity.
1. Set proper Account Type for the accounts.

Check out the below given animated tutorial.
<img class="screenshot" src="assets/chart_of_accounts_builder/images/coa_builder_fork.gif">

### 3. Create a chart from scratch

<img class="screenshot" src="assets/chart_of_accounts_builder/images/coa_builder_new.gif">

### 4. Account Types

To submit a chart, you need to identify / create all the accounts with following account types.

- **Bank:** The account group under which bank account will be created.
- **Cash:** The account group under which cash account will be created.
- **Cost of Goods Sold:** The account to book the accumulated total of all costs used to manufacture / purchase a product or service, sold by a company.
- **Depreciation:** The expense account to book the depreciation of teh fixed assets.
- **Expenses Included In Valuation:** The account to book the expenses (apart from direct material costs) included in landed cost of an item/product, used in Perpetual Inventory, .
- **Fixed Asset:** The account to maintain the costs of fixed assets.
- **Payable:** The account which represents the amount owed by a company to its creditors.
- **Receivable:** The account which represents the amount owed by a company by its debtors.
- **Stock:** The asset account for booking the inventory value.
- **Stock Adjustment:** An expense account to book any adjustment entry of stock/inventory, and generally comes at the same level of Cost of Goods Sold.
- **Stock Received But Not Billed:** A temporary liability account which holds the value of stock received but not billed yet and used in Perpetual Inventory.

### 6. Contribute a chart
After submission of a chart, the maintenance team of erpnext gets an automated email about it. Then they verify and test it at their end and after sucessful verification, it becomes a part of standard chart of accounts inside erpnext repository.
	
### 5. Download a submitted chart
After submitting a chart, you can download it as well for immediate use. After downloading, unzip the file and place it under `erpnext/accounts/doctype/account/chart_of_accounts/verified/` directory. The file name must be started with the country code. And then you can use it for creation of chart of accounts in your company.

<!-- no-sidebar -->
