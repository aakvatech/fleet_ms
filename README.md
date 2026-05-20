# VSD Fleet MS

## Business Summary

VSD Fleet MS is a Frappe and ERPNext application for transport and fleet operations. It helps a transport team manage fleet master data, cargo registration, transportation orders, manifests, trips, fuel requests, operational payments, vehicle inspections, and trip reporting from one ERPNext workspace.

The app is designed for businesses that run in-house trucks, trailers, drivers, and subcontracted transport operations. It connects transport activity to ERPNext records such as Customers, Suppliers, Items, Warehouses, Accounts, Cost Centers, Employees, Sales Invoices, Purchase Orders, Stock Entries, Journal Entries, Payment Entry drafts, and General Ledger entries.

Based on the repository evidence, this app should be treated as **ERPNext required** rather than a standalone Frappe app.

## Business Problems This App Solves

| Problem | How VSD Fleet MS Helps |
|---|---|
| Fleet records are spread across spreadsheets, chats, and paper files | Centralizes trucks, trailers, drivers, documents, cargo, routes, expenses, and settings in Frappe DocTypes |
| Cargo, manifests, trips, and invoices are hard to reconcile | Links cargo registration, manifests, trips, and Sales Invoices through transport-specific records |
| Trip fuel and petty cash requests lack operational context | Tracks fuel requests and requested funds against trips, drivers, trucks, customers, routes, and companies |
| Managers lack a live view of active trucks, idle trucks, trips, and payments | Provides a Fleet MS workspace, dashboard number cards, and trip/fuel reports |
| Vehicle assignment and trip execution are difficult to control | Supports transportation orders, vehicle assignment, manifests, trip creation, round trips, breakdowns, and resumption trips |
| Inspection readiness is not consistently documented | Provides inspection templates and truck/trailer inspection records with checklist-style child tables |

## Who This App Is For

| Organization / Team | Fit |
|---|---|
| Transport and logistics companies using ERPNext | Strong fit |
| Businesses managing own trucks, trailers, drivers, and subcontractors | Strong fit |
| Operations teams that need cargo, manifest, trip, fuel, and expense tracking | Strong fit |
| Finance teams that need transport expenses linked to ERPNext Accounts and Cost Centers | Strong fit |
| ERPNext implementers building a transport vertical solution | Strong fit |

## Who This App Is Not For

| Scenario | Reason |
|---|---|
| Companies not using ERPNext | The app imports ERPNext modules and uses ERPNext accounting, stock, selling, buying, HR, and master data records |
| Teams that only need simple vehicle maintenance logs | The app is broader than maintenance and includes cargo, manifests, trips, fuel, invoicing, and payments |
| Businesses needing a plug-and-play GPS integration without technical validation | The GPS connector exists, but its database connection and dependency setup need confirmation before production use |
| Teams needing a fully documented approval matrix out of the box | Roles and approval methods exist, but final workflow ownership should be confirmed during implementation |

## Business Benefits

| Benefit | Business Impact |
|---|---|
| Centralized fleet master data | Gives operations one place for trucks, trailers, drivers, routes, cargo types, locations, and fixed expenses |
| Cargo-to-trip traceability | Helps teams connect cargo registration, manifest preparation, trips, and invoice references |
| Fuel and fund request controls | Can improve visibility over trip cash, fuel supplier requests, approval status, and required accounting documents |
| ERPNext accounting integration | Connects transport costs to Accounts, Cost Centers, Accounting Dimensions, Journal Entries, Payment Entry drafts, and GL entries |
| Operational dashboards | Helps managers monitor active trucks, idle trucks, active trips, completed trips, requested payments, drivers, and fuel requests |
| Inspection records | Supports pre-trip or operational inspection routines for trucks and trailers |

## Before and After

| Before | After With VSD Fleet MS |
|---|---|
| Trips are planned in spreadsheets or informal communication | Trips are created as ERPNext records with route, driver, truck, manifest, fuel, funds, and status information |
| Cargo details are disconnected from billing | Cargo records can create or link Sales Invoices and carry cargo references into invoice items |
| Fuel requests are approved outside the trip context | Fuel requests are linked to trips and can create Purchase Orders or Stock Entries depending on settings |
| Trip cash is difficult to reconcile | Requested funds can move through recommendation, approval, accounts approval, payment reference, and accounting stages |
| Truck status changes are not auditable | Truck status changes create Truck Log entries |
| Managers wait for manual updates | Workspace cards, dashboard number cards, and reports provide operational visibility |

## Typical Use Cases

| Use Case | Supporting App Areas |
|---|---|
| Register cargo for a customer and prepare billing | Cargo Registration, Cargo Detail, Bulk Cargo, Sales Invoice creation |
| Create and assign transportation orders | Transportation Order, Transport Assignments, Trucks, Trailers, Truck Driver |
| Prepare a manifest and generate trips | Manifest, Manifest Cargo Details, Trips |
| Manage in-house and subcontracted trips | Manifest transporter type, Trips transporter fields, Transport Assignments |
| Request and approve fuel | Fuel Requests, Fuel Requests Table, Purchase Order, Stock Entry |
| Request and approve trip funds | Requested Payment, Requested Fund Details, Requested Fund Accounts Table, Journal Entry, Payment Entry |
| Configure route costs | Trip Routes, Route Steps, Fixed Expenses, Fixed Expenses Table |
| Inspect trucks and trailers | Truck Inspections Template, Truck and Trailer Inspection, checklist child tables |
| Track operational performance | Fleet MS workspace, Fleet Overview dashboard, Trip Report and Expenses, Fuel Expense By Trip |

## Example Business Workflow

1. Configure Transport Settings with fuel item groups, sales item groups, warehouse, expense account groups, cash or bank account groups, and accounting dimension rules.
2. Set up trucks, trailers, drivers, cargo types, trip locations, trip routes, fixed expenses, and inspection templates.
3. Register cargo or create a transportation order for a customer.
4. Assign vehicles, drivers, trailers, and subcontractor details where needed.
5. Prepare a manifest from cargo details and submit it.
6. Create or update trips from the manifest, including route steps, driver information, fuel requirements, and requested funds.
7. Review and approve fuel and fund requests.
8. Generate ERPNext documents where configured, such as Sales Invoices, Purchase Orders, Stock Entries, Journal Entries, Payment Entry drafts, and GL entries.
9. Monitor active trips, completed trips, trucks, drivers, payments, and fuel usage through the workspace, dashboard, and reports.

## ERPNext Value Addition

| ERPNext Area | Records / Capabilities Used | Evidence |
|---|---|---|
| Selling | Sales Invoice, Sales Invoice Item | Cargo Registration, Transportation Order, and Bulk Cargo contain Sales Invoice creation logic; patches add `cargo_id` to Sales Invoice Item |
| Buying | Purchase Order | Trips and fuel request tables support Purchase Order creation for approved fuel requests |
| Stock | Stock Entry, Warehouse, Item | Trips and Fuel Requests support stock movement for fuel; Transport Settings stores fuel item and warehouse configuration |
| Accounting | Account, Cost Center, Accounting Dimension, Journal Entry, Payment Entry, GL Entry | Requested Payment and Trips create or validate accounting entries and use ERPNext accounting utilities |
| Master Data | Company, Customer, Supplier, Item, Item Group, UOM, Currency, Country | DocType fields link transport records to ERPNext masters |
| HR | Employee | Truck Driver and payment/fund tables link drivers and payment recipients to Employee |

## Stand-alone Value

This repository does not provide enough evidence to describe the app as standalone. It uses Frappe DocTypes, workspaces, dashboards, reports, permissions, and form scripts, but it imports ERPNext Python modules and links heavily to ERPNext DocTypes. Install and evaluate it as an ERPNext app.

## Decision Guide

| Question | If Yes |
|---|---|
| Do you already run ERPNext for accounting, buying, selling, stock, or HR? | This app can extend your ERPNext site for transport operations |
| Do you manage cargo, manifests, trucks, trailers, drivers, and routes? | The app maps closely to your operational model |
| Do trip fuel and fund requests need approval and accounting visibility? | The Requested Payment and Fuel Requests flows are relevant |
| Do you need Sales Invoices linked to cargo or transport orders? | The app includes Sales Invoice creation from multiple transport records |
| Do you need simple fleet maintenance only? | This app may be more complex than needed |
| Do you need production GPS tracking immediately? | Confirm and harden the GPS connector before relying on it |

## Expected Business Outcomes

VSD Fleet MS can help improve transport record discipline, cargo-to-trip traceability, fuel and fund request visibility, and the connection between transport operations and ERPNext accounting. It can also help managers monitor fleet utilization and trip progress through dashboards and reports.

Actual outcomes depend on clean master data, agreed approval roles, correct ERPNext account setup, user adoption, and production testing of integrations.

## Screenshots / Visual Walkthrough

The previous README referenced this screenshot:

<img width="1672" height="941" alt="image" src="https://github.com/user-attachments/assets/411e29f6-80e6-42ad-87f8-5bc64c6fc69a" />

Recommended screenshots before publishing:

| Screenshot | Status |
|---|---|
| Fleet MS workspace | To confirm |
| Fleet Overview dashboard | To confirm |
| Trip form with route, fuel, and requested funds | To confirm |
| Manifest form | To confirm |
| Requested Payment approval flow | To confirm |
| Fuel Expense By Trip report | To confirm |

## Demo Scenario

1. Create or confirm a Company, Customer, Supplier, Item, fuel Item Group, Warehouse, Accounts, Cost Center, and Employee.
2. Configure Transport Settings.
3. Add a truck, trailer, truck driver, trip route, fixed expenses, and cargo type.
4. Create a Cargo Registration or Transportation Order.
5. Create a Manifest from available cargo.
6. Generate a Trip from the Manifest.
7. Add fuel and fund requests to the Trip.
8. Approve requests and generate the required ERPNext accounting, buying, stock, or payment records.
9. Review the Fleet Overview dashboard and trip reports.

## Implementation Effort

| Area | Effort | Notes |
|---|---|---|
| App installation | Low to Medium | Standard Frappe app installation once ERPNext compatibility is confirmed |
| Master data setup | Medium | Requires trucks, trailers, drivers, routes, locations, cargo types, accounts, warehouses, items, and employees |
| ERPNext accounting configuration | Medium to High | Accounts, Cost Centers, Accounting Dimensions, GL behavior, and payment workflows must be reviewed |
| User roles and approvals | Medium | Existing roles should be mapped to real operational responsibilities |
| Migration from spreadsheets | Depends | Requires mapping historical cargo, trips, trucks, drivers, and open requests |
| GPS integration | High / To confirm | Connector code exists but needs production validation |
| Training | Medium | Users need process training across operations, fuel, finance, and management reporting |

## What Needs to Be Ready Before Implementation

| Readiness Item | Why It Matters |
|---|---|
| ERPNext site with company and accounting masters | The app depends on ERPNext records and accounting utilities |
| Customer, Supplier, Item, Item Group, Warehouse, Account, Cost Center, Currency, and Employee data | Required by linked fields and automated document creation |
| Transport master data | Trucks, trailers, drivers, cargo types, routes, locations, and fixed expenses drive daily operations |
| Approval responsibilities | Fuel and requested payment actions require clear operational and accounts ownership |
| Chart of accounts and dimensions | Transport Settings can map accounting dimensions and restrict account groups |
| Fuel stock process | Purchase Order and Stock Entry behavior depends on warehouse, item, and supplier setup |
| Reporting expectations | Reports exist, but management KPIs and filters should be validated |

## Risks and Considerations

| Risk / Consideration | Recommendation |
|---|---|
| ERPNext dependency is not declared in `pyproject.toml` | Install ERPNext before this app and confirm target ERPNext/Frappe versions |
| Several whitelisted methods use `allow_guest=True` | Review authentication and permissions before production deployment |
| GPS connector appears incomplete or environment-specific | Confirm database connection, dependency packaging, DocType names, and security before enabling |
| Old README had conflicting license text | Repository metadata and `license.txt` state MIT; confirm before publishing externally |
| No active scheduler hooks are registered | If scheduler functions are needed, add and test scheduler configuration |
| Some integration assumptions depend on Transport Settings | Configure and test Purchase Order, Journal Entry, Stock Entry, and accounting toggles carefully |

## Frequently Asked Business Questions

### Do we need ERPNext?

Yes. The repository imports ERPNext modules and links to ERPNext accounting, stock, buying, selling, HR, and master data records.

### Will this replace ERPNext?

No. It extends ERPNext for transport and fleet operations.

### Can it be customized?

Yes. It is a Frappe app with DocTypes, form scripts, Python controllers, reports, patches, and settings. Customization should be done carefully because several flows create ERPNext accounting and stock documents.

### Can managers get reports?

Yes. The app includes a Fleet MS workspace, a Fleet Overview dashboard, number cards, and reports for trips and fuel expenses.

### Can existing spreadsheet data be migrated?

Likely yes, but the repository does not include migration templates. Data should be mapped to trucks, trailers, drivers, routes, cargo, manifests, trips, fuel requests, and requested payments before import.

### What should we prepare before implementation?

Prepare ERPNext master data, transport master data, account groups, warehouses, fuel items, roles, approval rules, and sample operational scenarios for testing.

---

## Key Features

- Fleet master data for trucks, trailers, truck drivers, truck types, cargo types, countries, locations, trip routes, fixed expenses, and fuel UOM.
- Cargo registration and bulk cargo handling with Sales Invoice creation.
- Transportation orders with assignment status and vehicle assignment support.
- Manifest preparation for in-house and subcontractor transport.
- Trip management with route steps, side trips, round trips, breakdowns, resumption trips, location updates, fuel requests, and requested funds.
- Fuel request approval with Purchase Order and Stock Entry support.
- Requested payment workflow with recommendation, approval, accounts approval, payment references, Payment Entry draft preparation, and GL entry handling.
- Truck and trailer inspection templates and checklist records.
- Transport Settings for item groups, warehouses, account groups, accounting dimension mapping, and required accounting controls.
- Fleet workspace, dashboard number cards, reports, and a sample print format.

## Compatibility

| Item | Value |
|---|---|
| App package name | `vsd_fleet_ms` |
| App title | `VSD Fleet MS` |
| App version | `14.0.6` from `vsd_fleet_ms/__init__.py` |
| Python | `>=3.10` from `pyproject.toml` |
| Frappe version | To confirm |
| ERPNext version | To confirm |
| ERPNext dependency | Required by code imports and linked ERPNext DocTypes |
| Node, MariaDB, Redis | Managed by the target Frappe/ERPNext bench |
| Extra Python dependencies | To confirm if GPS connector is used, because `psycopg2` is imported but no requirements file is present |

## App Mode

**ERPNext required.**

Evidence:

- `requested_payment.py` imports ERPNext accounting modules.
- `trips.py` imports `erpnext.setup.utils.get_exchange_rate`.
- DocTypes link to ERPNext records such as Company, Customer, Supplier, Item, Item Group, Warehouse, Account, Cost Center, Employee, Sales Invoice, Purchase Order, Stock Entry, Journal Entry, and Payment Entry.
- Patches add a custom field to `Sales Invoice Item`.

## Installation

Install ERPNext on the target site before installing this app.

```bash
cd /path/to/frappe-bench
bench get-app https://github.com/VVSD-LTD/vsd_fleet_ms.git
bench --site your-site.local install-app vsd_fleet_ms
bench --site your-site.local migrate
```

For local development from this checked-out folder:

```bash
cd /path/to/frappe-bench
bench get-app /path/to/this-repository
bench --site your-site.local install-app vsd_fleet_ms
bench --site your-site.local migrate
```

## Configuration

Configure `Transport Settings` before using operational flows.

| Setting Area | Fields / Tables |
|---|---|
| Fuel and stock | Vehicle Fuel Parent Warehouse, Fuel Item, Fuel Item Group |
| Sales | Sales Item Group |
| Accounts | Expense Account Group, Cash or Bank Account Group |
| Controls | Require Purchase Order For Fuel, Require Journal Entry For Funds |
| Dimensions | Accounting Dimension mapping table |
| Service integration | Enable Service MS Integration |
| Capacity defaults | Default Compartment Capacity |

Recommended setup order:

1. ERPNext Company, Customers, Suppliers, Items, Item Groups, Warehouses, Accounts, Cost Centers, Employees, UOMs, and Currencies.
2. Transport Settings.
3. Cargo Types, Countries, Transport Locations, Trip Locations, Trip Locations Type, Trip Routes, Fixed Expenses.
4. Trucks, Trailers, Truck Drivers, and Truck Inspection Templates.
5. Operational transactions: Cargo Registration, Transportation Order, Manifest, Trips, Fuel Requests, Requested Payment.

## Usage

1. Open the `Fleet MS` workspace.
2. Create the required master data.
3. Register cargo or create a transportation order.
4. Assign transport resources.
5. Create a manifest and generate trips.
6. Add fuel requests and requested funds to the trip.
7. Process approvals and create ERPNext documents as needed.
8. Review dashboards and reports.

## Modules and DocTypes

### Main DocTypes

| DocType | Purpose |
|---|---|
| Transport Settings | Central settings for fuel, sales, account groups, dimensions, and required controls |
| Truck | Truck master with status, driver, fuel warehouse, documents, and compartments |
| Trailers | Trailer master with plate, status, type, suspension, compartments, and documents |
| Truck Driver | Driver master linked to Employee |
| Trip Routes | Route master with route steps, fixed expenses, distance, fuel, and cost totals |
| Fixed Expenses | Expense master linked to expense and cash/bank accounts |
| Cargo Registration | Customer cargo registration with cargo detail rows and Sales Invoice creation support |
| Bulk Cargo | Bulk cargo transaction with capacity tracking and Sales Invoice creation support |
| Transportation Order | Customer transport order with cargo rows and assignment status |
| Manifest | Manifest preparation for cargo, truck, trailer, driver, and route details |
| Trips | Core trip record for route execution, fuel, funds, status, stock, journal entries, inspections, and breakdowns |
| Fuel Requests | Fuel request and approval record linked to a trip or reference document |
| Requested Payment | Fund request and accounts approval record linked to trip or reference document |
| Round Trip | Groups related trip records |
| Trip Breakdown | Creates breakdown and resumption flows for trips |
| Truck and Trailer Inspection | Inspection record linked to trip and inspection template |
| Truck Inspections Template | Checklist template for truck and trailer inspection sections |
| Truck Log | Status-change log for trucks |

### Child Tables and Supporting DocTypes

The app also defines child tables for cargo details, cargo trips, manifest cargo details, transport assignments, requested fund details, requested fund accounts, reference payments, fuel request rows, route steps, trip steps, side trips, vehicle trip rows, documents, compartments, accounting dimensions, and detailed inspection checklist sections.

## ERPNext Integration Details

| Flow | ERPNext Integration |
|---|---|
| Cargo billing | Creates Sales Invoices from Cargo Registration, Transportation Order, and Bulk Cargo |
| Cargo-invoice traceability | Adds `cargo_id` custom field to Sales Invoice Item |
| Trip fuel procurement | Can create Purchase Orders from approved fuel request rows |
| Fuel stock movement | Can create Stock Entries for fuel stock-out |
| Trip fund accounting | Can create Journal Entries and GL Entries for approved requested funds |
| Payment processing | Can prepare Payment Entry drafts for requested payments |
| Accounting dimensions | Maps source transport fields to target ERPNext document fields using Transport Settings |
| Driver and payee linkage | Uses Employee links for drivers and payment recipients |

## Custom Fields and Fixtures

No `fixtures` directory or active `fixtures` hook was found.

Patch files create or update:

| Patch | Effect |
|---|---|
| `add_cargo_id_custom_field_on_sales_invoice_item.py` | Adds read-only `Cargo ID` field to Sales Invoice Item |
| `add_bill_uom_field_in_cargo_detail.py` | Adds `Bill UOM` and `Net Weight (Tonne)` to Cargo Detail |
| `add_allow_bill_on_weight.py` | Adds `Allow Bill On weight` to Cargo Detail |
| `create_property_setter_cargo_details.py` | Allows Cargo Registration cargo details to be updated on submit |

## Permissions

| Area | Roles Found |
|---|---|
| Most master and transaction DocTypes | System Manager |
| Cargo Registration, Manifest, Trips | All, System Manager |
| Requested Payment | Expense Approver, Expense Recommender, System Manager |
| Truck Driver | Fleet Manager, HR Manager, HR User |
| Cargo Types | Clearing Agent |

Review role access before production, especially because several API methods are guest-accessible.

## Reports and Dashboards

| Asset | Type | Notes |
|---|---|---|
| Fleet MS | Workspace | Includes cards for Masters, Trips, Settings, Transactions, Transport Records, and Reports |
| Fleet Overview | Dashboard | Standard dashboard with number cards for active trucks, idle trucks, active trips, completed trips, requested payments, drivers, and total fuel requested |
| Trip Report and Expenses | Script Report | Trip expense report with date filters |
| Fuel Expense By Trip | Script Report | Fuel request and trip cost report |
| Trips Report | Report Builder | Report Builder report on Trips |
| Joel Print Sample | Print Format | Sample print format included in repository |

## APIs

The app exposes multiple whitelisted server methods from DocType controllers.

| Area | Examples |
|---|---|
| Cargo | Create Sales Invoice from Cargo Registration; create Cargo Registration and Sales Invoice from Bulk Cargo |
| Transportation Order | Create transport orders, assign vehicles, create Sales Invoices |
| Manifest | Get manifests, create new manifest, add cargo to existing manifest |
| Trips | Create trip from manifest, create fund Journal Entry, create stock-out entry, create Purchase Order, create breakdown and resumption trip, create vehicle inspection |
| Fuel Requests | Approve, reject, update status, and create Stock Entry |
| Requested Payment | Request funds, recommend, approve, reject, accounts approve/cancel, create payment reference, prepare a Payment Entry draft |
| GPS Connector | Get last location, load cargo, offload cargo, loop through vehicles |

Security note: several methods are decorated with `@frappe.whitelist(allow_guest=True)`. These should be reviewed and restricted where appropriate before production use.

## Hooks and Events

`hooks.py` contains app metadata only. No active `doc_events`, `scheduler_events`, `fixtures`, `doctype_js`, `override_doctype_class`, install hooks, or uninstall hooks are registered there.

Business behavior is implemented mainly in DocType controller methods and form scripts:

| Area | Examples |
|---|---|
| DocType lifecycle methods | `validate`, `before_save`, `before_submit`, `on_submit`, `after_insert`, `on_update` |
| Form scripts | Custom buttons, field filters, child-row logic, and UI actions in DocType `.js` files |
| Patches | Custom fields and property setters applied during migration |

## Background Jobs

No scheduler events are registered in `hooks.py`.

The repository includes callable functions that look scheduler-oriented, such as `transport_order_scheduler()` and `loop_through_vehicles()`, but they are not wired into Frappe scheduler configuration in this repository.

## Developer Setup

```bash
cd /path/to/frappe-bench
bench get-app /path/to/this-repository
bench --site your-site.local install-app vsd_fleet_ms
bench --site your-site.local migrate
bench --site your-site.local run-tests --app vsd_fleet_ms
```

Developer notes:

- The package uses `pyproject.toml` with `flit_core`.
- App metadata is in `vsd_fleet_ms/hooks.py`.
- App version is in `vsd_fleet_ms/__init__.py`.
- Tests exist for several DocTypes, but test coverage depth should be confirmed.

## Project Structure

```text
vsd_fleet_ms/
  hooks.py
  modules.txt
  patches.txt
  custom/
  utils/
  config/
  patches/
    custom_fields/
    property_setters/
  vsd_fleet_ms/
    doctype/
    report/
    workspace/
    print_format/
    vsd_fleet_ms_dashboard/
```

## Migration Notes

Run migrations after installing or updating the app:

```bash
bench --site your-site.local migrate
```

Migration patches create custom fields for Sales Invoice Item and Cargo Detail and set Cargo Registration cargo details to allow updates after submit. Review these changes before deploying to a production ERPNext site with existing customizations.

## Upgrade Guide

1. Back up the ERPNext site.
2. Pull or update the app code.
3. Review pending patches in `vsd_fleet_ms/patches.txt`.
4. Run `bench --site your-site.local migrate`.
5. Test Cargo Registration, Transportation Order, Manifest, Trips, Fuel Requests, Requested Payment, and reports in a staging site.
6. Confirm custom fields and accounting behavior after migration.

## Uninstallation

No custom uninstall hook is registered in `hooks.py`.

Before uninstalling:

1. Back up the site.
2. Review submitted transport documents and linked ERPNext documents.
3. Confirm whether custom fields on Sales Invoice Item and Cargo Detail should remain.
4. Run the standard Frappe uninstall process only after business approval.

```bash
bench --site your-site.local uninstall-app vsd_fleet_ms
```

## Troubleshooting

| Issue | What to Check |
|---|---|
| App fails because ERPNext modules are missing | Install ERPNext before installing VSD Fleet MS |
| Sales Invoice creation fails | Check Customer, service item, Sales Item Group, cargo rows, and company setup |
| Purchase Order creation for fuel fails | Check Transport Settings, fuel item, supplier, warehouse, and request status |
| Stock Entry creation fails | Check Truck fuel warehouse, fuel item, quantity, and stock settings |
| Journal Entry or GL entry fails | Check Account, Cost Center, Company currency, Accounting Dimensions, approval status, and required settings |
| Reports show unexpected results | Validate report filters, trip status values, and submitted request data |
| GPS methods fail | Confirm connector database connection, `psycopg2`, expected GPS schema, and DocType names |

## Security

Review the following before production deployment:

- Guest-accessible whitelisted methods in fuel requests, requested payments, trips, GPS connector, and transportation order flows.
- Accounting functions that create GL entries and Journal Entries, and prepare Payment Entry drafts.
- Permissions for Cargo Registration, Manifest, and Trips where the `All` role appears.
- Data exposure through dashboards, reports, and guest methods.
- Any deployment-specific GPS credentials or external database access.

## Repository Evidence Reviewed

| File / Area | Evidence Found |
|---|---|
| `pyproject.toml` | Package name, publisher, Python version, project description, readme target |
| `vsd_fleet_ms/__init__.py` | App version `14.0.6` |
| `vsd_fleet_ms/hooks.py` | App metadata, MIT license, no active scheduler or document hooks |
| `license.txt` | MIT license |
| `vsd_fleet_ms/modules.txt` | App modules: VSD Fleet MS and Fleet Managment |
| `vsd_fleet_ms/patches.txt` | Custom field and property setter patches |
| `vsd_fleet_ms/vsd_fleet_ms/doctype/**/*.json` | DocType fields, roles, links, child tables, submit behavior, select options |
| `cargo_registration.py`, `transportation_order.py`, `bulk_cargo.py` | Sales Invoice creation logic |
| `trips.py` | Trip lifecycle, fuel request generation, Journal Entry, Stock Entry, Purchase Order, inspection, breakdown, and resumption logic |
| `requested_payment.py` | ERPNext accounting imports, requested fund workflow, GL, Payment Entry, approval and payment logic |
| `fuel_requests.py` | Fuel request status and Stock Entry creation |
| `manifest.py` | Manifest validation, cargo allocation, trip update, cargo registration update, Sales Invoice item dimension logic |
| `custom/custom_functions.py` | Child-table sync override and cargo-to-manifest query |
| `utils/dimension.py` | Transport Settings accounting dimension mapping |
| `gps_connector.py` | GPS connector methods and guest-accessible endpoints |
| `workspace/fleet_ms/fleet_ms.json` | Fleet MS workspace links and number cards |
| `vsd_fleet_ms_dashboard/fleet_overview/fleet_overview.json` | Fleet Overview dashboard |
| `report/**` | Trip, expense, and fuel reports |

## To Confirm Before Publishing

- Exact supported Frappe and ERPNext versions.
- Whether this repository is intended for ERPNext version 15 despite app version `14.0.6`.
- Final public repository URL and branch strategy.
- Production screenshot set.
- Whether Service MS Integration requires another app that should be documented as a dependency.
- GPS connector readiness, credentials, dependency packaging, and security model.
- Final role and approval matrix for fuel, requested funds, accounts approval, and operations.
- Whether guest-accessible API methods should remain public.
- Whether old README license text mentioning GPL should be ignored in favor of MIT metadata and `license.txt`.
- Maintainer contacts and support process.

## Support and Maintenance

Current metadata lists:

| Item | Value |
|---|---|
| Publisher | VV SYSTEMS DEVELOPER LTD |
| Email | info@vvsdtz.com |
| App title | VSD Fleet MS |

For support, use the repository issue tracker or the maintainer contact above once the public support process is confirmed.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make a focused change.
4. Run relevant Frappe tests.
5. Open a pull request with a clear explanation, migration notes, and screenshots for UI changes.

```bash
git checkout -b feature/your-change
bench --site your-site.local run-tests --app vsd_fleet_ms
```

## Versioning

The current app version is `14.0.6` in `vsd_fleet_ms/__init__.py`.

Use semantic or Frappe-app-style versioning consistently and document breaking changes, patches, and ERPNext compatibility for each release.

## License

MIT, based on `license.txt` and `app_license = "MIT"` in `hooks.py`.

## Maintainers

| Maintainer | Contact |
|---|---|
| VV SYSTEMS DEVELOPER LTD | info@vvsdtz.com |
