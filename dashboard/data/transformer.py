def build_zone_capacity(tot_z, new_z):
    total = tot_z.groupby(["z", "g"])["value"].sum().reset_index(name="total")
    new = new_z.groupby(["z", "g"])["value"].sum().reset_index(name="new")

    df = total.merge(new, on=["z", "g"], how="left")
    df["new"] = df["new"].fillna(0)
    df["existing"] = df["total"] - df["new"]
    return df