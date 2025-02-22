import os
import pandas as pd
import random

folder_path = "/home/meri/SharedFolder/out"
columns = ["FilePath", "label"]
data= []
d_df = {}
ilistdir = os.listdir(folder_path)
d_df["FilePath"] = []
d_df["Label"] = []
for filename in listdir:
    d_df["FilePath"].append(os.path.join(folder_path, filename))
    d_df["Label"].append(filename.split("_")[5][0:3] == "tum")

df = pd.DataFrame(d_df)
df.to_csv("patch_data.csv", index=False)



