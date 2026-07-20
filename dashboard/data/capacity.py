from data_loader import table


def capacity_summary(df, sets):
    vre_table = table(sets, "vre")
    vre_techs = list(vre_table["g"])
    total_all = df["var_tot_pcap"]
    new_all = df["var_new_pcap"]

    installed_vre = total_all[total_all["g"].isin(vre_techs)]
    installed_new_vre = new_all[new_all["g"].isin(vre_techs)]

    return {
        "total_installed": total_all["value"].sum().round(0),
        "new_installed": new_all["value"].sum().round(0),
        "total_vre": installed_vre["value"].sum().round(0),
        "new_vre": installed_new_vre["value"].sum().round(0),
    }
