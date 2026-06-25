import numpy as np

def remove_duplicate_pairs(df):
    df[['z', 'z_alias']] = np.sort(df[['z', 'z_alias']], axis=1)
    df = df.drop_duplicates().reset_index(drop=True)
    return df
