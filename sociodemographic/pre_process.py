import pandas as pd
import os

#df = pd.read_csv('/scratch/tyoeasley/WAPIAW3/sociodemographic/output_only_social.csv',index_col=None, header=0)
#df = df.iloc[:, :-3]

#replacement of missing information with the median value calculated from the known part of the variable
#for col in df.columns:
#    median = df[col].median()
#    df[col].fillna(median, inplace=True)

df=pd.read_csv('output_only_social.csv',index_col=None)
base_path = '/scratch/tyoeasley/WAPIAW3/brainrep_data/SocialDemo_data/Social/'
print(df)
for index, row in df.iterrows():
    filename = "sub-" + str(int(row['eid']))
    row_df = pd.DataFrame(row[2:]).T
    print(row_df)

    row_df.to_csv(base_path+filename + '.csv', index=False,header = False)
