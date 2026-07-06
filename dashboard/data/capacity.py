from data.constants import VRE_TECHS


def capacity_summary(df):
    total_all = df["var_tot_pcap"]
    new_all = df["var_new_pcap"]

    installed_vre = total_all[total_all["g"].isin(VRE_TECHS)]
    installed_new_vre = new_all[new_all["g"].isin(VRE_TECHS)]

    return {
        "total_installed": total_all["value"].sum().round(0),
        "new_installed": new_all["value"].sum().round(0),
        "total_vre": installed_vre["value"].sum().round(0),
        "new_vre": installed_new_vre["value"].sum().round(0),
    }
