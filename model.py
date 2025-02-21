import os
import pandas as pd
import random

folder_path = "/home/meri/SharedFolder/out"
columns = ["FilePath", "label"]
data= []
for filename in os.listdir(folder_path):
    data.append([os.path.join(folder_path, filename), filename.split("_")[5][0:4] == "tum"])

df = pd.DataFrame(data, columns)

df.to_csv("patch_data.csv", index=false)
print("hello")
print(df.head())
