<div align="center">

# Fleet MS

**Fleet & Transport Management for ERPNext**

Manage fleets, cargo, trips, fuel, tyres and transport finances in one connected platform.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](license.txt)
[![ERPNext v15](https://img.shields.io/badge/ERPNext-v15-green.svg)](https://erpnext.com/)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Frappe Framework](https://img.shields.io/badge/Frappe-Framework-orange.svg)](https://frappeframework.com/)

</div>

<div align="center">

<p><strong>🚛 Fleet Operations &nbsp;&nbsp;&nbsp; 🗺️ Trips &amp; Cargo &nbsp;&nbsp;&nbsp; ⛽ Fuel &amp; Expenses</strong></p>

<p><strong>🛞 Tyre Tracking &nbsp;&nbsp;&nbsp; 📊 Analytics &nbsp;&nbsp;&nbsp; 🔗 Integrations</strong></p>

</div>

<p align="right"><sub>by <a href="https://www.aakvatech.com">Aakvatech</a></sub></p>

## About Fleet MS

Fleet MS is an open-source fleet and transport management application for logistics companies and fleet operators. Built on ERPNext and the Frappe Framework, it connects transport operations with accounting, buying, selling and inventory.

## Key Features

- **Fleet Management:** Maintain truck and trailer specifications, driver profiles, vehicle documents, inspections and fleet availability to support daily transport operations.
- **Cargo & Transport Orders:** Register customer cargo, create transportation orders, prepare manifests and coordinate vehicle and driver assignments for dispatch.
- **Trips & Routes:** Manage routes, destinations, trip assignments, round trips and side trips, including breakdown handling and journey resumption.
- **Fuel & Expenses:** Control fuel requests, consumption, trip expenses, operational fund requests and approvals, with related ERPNext accounting, purchasing and stock transactions.
- **Tyre Tracking:** Manage tyre records, installation, removal, position changes, transfers, inspections, usage and movement history throughout the tyre lifecycle.
- **Reporting:** Monitor fleet utilization, trip revenue and profitability, fuel consumption, turnaround times and operational performance through dashboards and reports.

## Operational Flow

Fleet MS brings transport planning, vehicle and driver assignment, trip execution, operational controls and ERPNext financial reporting into one coordinated workflow.

## ERPNext & Optional Integrations

Fleet MS extends **ERPNext Accounting, Selling, Buying and Stock** workflows.

- **CSF_TZ (Tanzania):** An independent companion application for Traffic, TIRA and LATRA compliance records, subject to separate installation and configuration. This is not a built-in Fleet MS feature.
- **Service MS:** An independent maintenance application for servicing and Service Job Cards, with optional Service Job Card-driven tyre movements. Install and configure it separately.

## Installation

**Requirements:** Frappe Framework v15, ERPNext v15 and a compatible Python environment.

```bash
bench get-app --branch version-15-hotfix https://github.com/aakvatech/fleet_ms.git
bench --site your-site.local install-app vsd_fleet_ms
bench --site your-site.local migrate
```

After installation, configure Transport Settings, fleet masters, permissions and the required ERPNext accounts and warehouses.

The technical application identifier is `vsd_fleet_ms`.

## Support & Contributions

Report issues and propose improvements through the [Fleet MS repository](https://github.com/aakvatech/fleet_ms). Fleet MS is maintained and enhanced by **Aakvatech**.

## Credits & License

Originally developed by **[VV SYSTEMS DEVELOPER LTD (VVSD)](https://vvsdtz.com/)**, Tanzania. Fleet MS is a fork of the original VSD Fleet project; we acknowledge VVSD and the original contributors.

Licensed under the **MIT License**. See [license.txt](license.txt).
