# Fleet MS

**Fleet and transport operations management for ERPNext / Frappe v15**

Fleet MS is an ERPNext application for transport and fleet operations. It brings vehicles, drivers, cargo, transport orders, manifests, trips, fuel, operational payments, inspections, tyre management, dashboards, and transport reporting into one ERPNext environment.

The app is intended for transport and logistics companies, private fleets, and organizations that need operational fleet records to work together with ERPNext accounting, buying, selling, stock, HR, and master data.

> **App package:** `vsd_fleet_ms`  
> **App version:** `15.0.0`  
> **Frappe compatibility:** `>=15.0.0,<16.0.0`  
> **ERPNext:** Required by the application's operational and accounting integrations  
> **License:** MIT

---

## What Fleet MS Covers

Fleet MS connects the operational transport cycle from fleet setup to trip execution and financial follow-up.

### Fleet Masters

Maintain the core records used by transport operations, including:

- Trucks and trailers
- Truck drivers
- Vehicle and truck types
- Cargo types
- Transport and trip locations
- Trip routes and route steps
- Fixed trip expenses
- Fuel-related configuration
- Vehicle documents and operational details

### Cargo and Transport Orders

Capture customer transport requirements and connect them to operational execution.

Key capabilities include:

- Cargo registration
- Bulk cargo handling
- Transportation orders
- Cargo details and quantities
- Customer and route information
- Vehicle assignment
- Sales Invoice integration where supported by the transaction flow

### Manifest Management

Prepare transport manifests using registered cargo and assigned transport resources.

Manifests can bring together:

- Cargo
- Customer information
- Truck and trailer
- Driver
- Route
- Transporter information
- In-house and subcontracted transport activity

### Trip Management

Trips are the operational center of Fleet MS.

The application supports trip information such as:

- Origin and destination
- Route and route steps
- Truck, trailer, and driver
- Customer and cargo references
- Trip status and location updates
- Fuel requirements
- Requested operational funds
- Fixed and variable trip expenses
- Round-trip and side-trip handling
- Breakdown and resumption scenarios

### Fuel Management

Fuel requests are linked to fleet operations and trips rather than being handled as isolated requests.

Depending on configuration, Fleet MS can support:

- Fuel request preparation
- Fuel approval
- Fuel item and warehouse controls
- Supplier-related fuel processing
- Purchase Order creation
- Stock Entry integration
- Trip fuel-cost reporting
- Fuel-consumption reporting

### Requested Payments and Trip Funds

Operational cash and payment requests can be recorded against transport activity.

The application includes workflows and data structures for:

- Requested funds
- Recommendation and approval
- Accounts review
- Payment references
- Expense-account allocation
- Cost-center and accounting-dimension context
- Journal Entry integration
- Payment Entry preparation / references
- General Ledger-related processing where implemented by the transaction flow

### Vehicle Inspections

Fleet MS includes inspection records and templates for trucks and trailers, allowing operations teams to maintain repeatable inspection checklists and inspection history.

### Tyre Management

The v15 application also contains a dedicated **Tyre Management** module and workspace.

Tyre-related functionality is integrated with fleet/service operations, including hooks for Service Job Card tyre movements when the corresponding Service Job Card functionality is available on the site.

### Dashboards and Reports

The repository includes Fleet Management and Tyre Management workspaces, a Fleet Overview dashboard, number cards, and operational reports.

Reports currently present in the app include:

- Fleet Performance
- Fuel Consumption Report
- Ongoing Trips Report
- Pending Fuel Requests Report
- Pending Requested Payments Report
- Trip Fuel Cost
- Trip Invoices Report
- Trip Profit and Loss Statement
- Trip Report and Expenses
- Trip Revenue Report
- Trip Turnaround Time
- Trips Report
- Vehicle Utilization

Available reports may depend on permissions, configuration, and the data captured by each implementation.

---

## Typical Operational Flow

A normal implementation can follow this process:

1. Configure ERPNext company, customers, suppliers, items, warehouses, accounts, cost centers, employees, currencies, and other required masters.
2. Configure **Transport Settings**.
3. Create fleet masters such as trucks, trailers, drivers, locations, routes, cargo types, and fixed expenses.
4. Register cargo or create a transportation order.
5. Assign the required transport resources.
6. Prepare and submit a manifest.
7. Create and manage the trip.
8. Record fuel requirements and operational fund requests.
9. Process approvals and create the required ERPNext stock, buying, accounting, or payment documents.
10. Monitor operations using Fleet MS workspaces, dashboards, and reports.

---

## ERPNext Integration

Fleet MS is designed as an **ERPNext extension**, not as a standalone Frappe application.

The codebase integrates transport operations with ERPNext records and utilities including:

| ERPNext Area | Examples |
| --- | --- |
| Selling | Customer, Sales Invoice, Sales Invoice Item |
| Buying | Supplier, Purchase Order |
| Stock | Item, Item Group, Warehouse, Stock Entry |
| Accounting | Account, Cost Center, Accounting Dimensions, Journal Entry, Payment Entry, GL-related processing |
| HR / People | Employee |
| Organization | Company, Currency and related masters |

Because these integrations are part of operational workflows, install and test Fleet MS together with the ERPNext version used by your site.

---

## Compatibility

| Component | Supported / Declared |
| --- | --- |
| Frappe Framework | `>=15.0.0,<16.0.0` |
| Fleet MS app version | `15.0.0` |
| Python | `>=3.10` |
| ERPNext | Required |
| App package | `vsd_fleet_ms` |
| License | MIT |

The Frappe dependency above is declared in `pyproject.toml`.

ERPNext is required by the application code and linked DocTypes, even though it is not currently declared as a Bench dependency in `pyproject.toml`.

---

## Installation

### Prerequisites

Before installing Fleet MS:

- Prepare a working **Frappe v15 / ERPNext v15** bench and site.
- Ensure the site has the ERPNext masters needed by your intended Fleet MS workflows.
- Take a backup before installing or upgrading on an existing production site.

### Install from GitHub

From your bench directory:

```bash
bench get-app --branch version-15 https://github.com/aakvatech/fleet_ms.git
bench --site your-site.local install-app vsd_fleet_ms
bench --site your-site.local migrate
```

Then rebuild/restart the bench as appropriate for your deployment:

```bash
bench build --app vsd_fleet_ms
bench restart
```

For managed hosting, use the deployment procedure supported by your hosting platform.

---

## Updating

Before updating a production site, review changes and take a backup.

```bash
cd /path/to/frappe-bench/apps/vsd_fleet_ms
git checkout version-15
git pull --ff-only origin version-15

cd /path/to/frappe-bench
bench --site your-site.local migrate
bench build --app vsd_fleet_ms
bench restart
```

If your deployment system manages Git revisions automatically, follow that system's update process instead.

---

## Initial Configuration

After installation, start with **Transport Settings** and your ERPNext masters.

Typical configuration areas include:

- Fuel item and fuel item group
- Vehicle fuel warehouse / parent warehouse
- Sales item group
- Expense account groups
- Cash or bank account groups
- Fuel Purchase Order requirements
- Fund Journal Entry requirements
- Accounting-dimension mapping
- Service MS integration option
- Default compartment capacity

A recommended setup order is:

1. ERPNext Company and accounting configuration
2. Customers and Suppliers
3. Items, Item Groups and UOMs
4. Warehouses
5. Accounts, Cost Centers and Accounting Dimensions
6. Employees / drivers
7. Transport Settings
8. Trucks and trailers
9. Cargo types and locations
10. Routes and fixed expenses
11. Inspection templates
12. User roles and permissions
13. End-to-end test transactions

---

## Workspaces

The repository currently includes these workspace areas:

### Fleet Management

The main operational workspace for fleet and transport transactions, masters, dashboards, and reports.

### Tyre Management

A dedicated workspace for tyre-related fleet operations.

---

## Service Job Card Integration

Fleet MS contains integration hooks and migration/install utilities related to **Service Job Card** tyre fields and trip references.

The app registers an `on_submit` hook for Service Job Card to create tyre movement information through Fleet MS integration logic.

If your site uses this integration, validate the corresponding Service Job Card DocType/app and the complete workflow in a staging environment before enabling it in production.

---

## Development

Clone/install the app into a Frappe v15 bench and use the standard Frappe development workflow.

The repository includes development tooling for code quality, including pre-commit configuration and Ruff settings.

Install development dependencies as appropriate for your environment and run the repository's configured checks before submitting changes.

Useful commands may include:

```bash
pre-commit run --all-files
ruff check .
ruff format --check .
```

Use the project's actual CI configuration as the final source of truth for required checks.

---

## Repository Structure

A simplified view of the repository:

```text
fleet_ms/
├── pyproject.toml
├── README.md
├── license.txt
├── scripts/
└── vsd_fleet_ms/
    ├── hooks.py
    ├── modules.txt
    ├── patches.txt
    ├── public/
    ├── utils/
    ├── www/
    └── vsd_fleet_ms/
        ├── doctype/
        ├── report/
        ├── workspace/
        └── vsd_fleet_ms_dashboard/
```

---

## Production Checklist

Before go-live, validate at least the following:

- Company and chart of accounts
- Cost centers and accounting dimensions
- Customers and suppliers
- Fuel items and warehouses
- Trucks, trailers, drivers, routes, and locations
- User roles and permissions
- Cargo-to-manifest-to-trip workflow
- Fuel request approval and document creation
- Requested payment approval and accounting flow
- Sales Invoice integration used by your process
- Stock Entry / Purchase Order behavior
- Service Job Card integration, if used
- Tyre Management workflow, if used
- Reports and dashboard permissions
- Print formats and operational documents
- Backup and recovery procedure

Always validate financial and stock postings in a staging/UAT site before production rollout.

---

## Security and Implementation Notes

Fleet MS contains business logic that can create or interact with accounting, stock, buying, and selling documents. Production deployments should therefore include a review of:

- Roles and permissions
- Approval responsibilities
- Whitelisted/API methods
- Accounting mappings
- Stock and warehouse controls
- Custom integrations
- Any external/GPS connectivity enabled for the deployment

Do not assume a default configuration is suitable for every company.

---

## Contributing

Contributions should target the appropriate maintained branch and should be tested against the supported Frappe/ERPNext version.

Recommended contribution flow:

1. Create a feature/fix branch.
2. Make focused changes.
3. Run the configured formatting, linting, security, and test checks.
4. Open a pull request with a clear description and test evidence.
5. Avoid committing environment-specific credentials, site configuration, or production data.

---

## Support

For implementation, customization, integration, or deployment support, open an issue in this repository or contact the project maintainers through the appropriate Aakvatech support channel.

Repository: https://github.com/aakvatech/fleet_ms

---

## Credits and License

Fleet MS was forked from the original **VSD Fleet** project. We acknowledge its original developers and contributors. The GitHub fork relationship and project history preserve this attribution.

MIT. See `license.txt`.

---

### Important

Fleet MS affects operational, stock, and financial processes. Always test upgrades and configuration changes on a staging/UAT site and take a current backup before applying them to production.
