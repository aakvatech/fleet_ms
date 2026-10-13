<div align="center">

# Fleet MS

**Fleet & Transport Management for ERPNext**

Manage fleets, cargo, trips, fuel, tyres and transport finances in one connected platform.

**ERPNext** · **Frappe Framework** · **Open Source** · **MIT License**

</div>

<table>
<tr>
<td align="center">🚛<br><b>Fleet Operations</b></td>
<td align="center">🗺️<br><b>Trips & Cargo</b></td>
<td align="center">⛽<br><b>Fuel & Expenses</b></td>
</tr>
<tr>
<td align="center">🛞<br><b>Tyre Tracking</b></td>
<td align="center">📊<br><b>Analytics</b></td>
<td align="center">🔗<br><b>Integrations</b></td>
</tr>
</table>

<p align="right"><sub>by <a href="https://www.aakvatech.com">Aakvatech</a></sub></p>

## About Fleet MS

Fleet MS is an open-source fleet and transport management application for logistics companies and fleet operators. Built on ERPNext and the Frappe Framework, it connects transport operations with accounting, buying, selling and inventory.

## Key Features

- **Fleet Management:** Manage trucks, trailers, drivers, vehicle records and inspections.
- **Cargo & Transport Orders:** Register cargo, organize transport orders and prepare manifests.
- **Trips & Routes:** Plan routes, assign resources and track trips, including side trips and breakdowns.
- **Fuel & Expenses:** Manage fuel requests, operational funds, approvals and trip costs.
- **Tyre Tracking:** Record truck tyre details and inspection checklists. The dedicated Tyre Lifecycle module is not included in this branch.
- **Reporting:** Analyze trips, fuel consumption, utilization, revenue and transport profitability.

## ERPNext & Optional Integrations

Fleet MS extends **ERPNext Accounting, Selling, Buying and Stock** workflows.

- **CSF_TZ (Tanzania):** An independent companion application for Traffic, TIRA and LATRA compliance records, subject to separate installation and configuration. This is not a built-in Fleet MS feature.
- **Service MS:** An independent maintenance application for servicing and Service Job Cards. Install and configure it separately.

## Installation

**Requirements:** Frappe Framework v15, ERPNext v15 and a compatible Python environment.

```bash
bench get-app --branch version-15 https://github.com/aakvatech/fleet_ms.git
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
