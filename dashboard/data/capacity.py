from data_loader import table


def capacity_summary(df, sets, adjusted_gbp=None):
    vre_table = table(sets, "vre")
    vre_techs = list(vre_table["g"])
    total_all = df["var_tot_pcap"]
    new_all = df["var_new_pcap"]

    installed_vre = total_all[total_all["g"].isin(vre_techs)]
    installed_new_vre = new_all[new_all["g"].isin(vre_techs)]

    storage_df = df["var_tot_store_pcap"]
    tot_storage = storage_df["value"].sum()

    if adjusted_gbp:
        demand_df = df["demand"]
        total_demand_gwh = demand_df["value"].sum()
        cost_per_mwh = adjusted_gbp / (total_demand_gwh * 1000)
    else:
        cost_per_mwh = None
    return {
        "total_installed": total_all["value"].sum().round(0),
        "new_installed": new_all["value"].sum().round(0),
        "total_vre": installed_vre["value"].sum().round(0),
        "new_vre": installed_new_vre["value"].sum().round(0),
        "tot_storage": tot_storage.round(0),
        "by_demand": cost_per_mwh,
    }
