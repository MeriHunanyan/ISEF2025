import pandas as pd
import shutil
import os
from tensorflow import keras
from tensorflow.keras import layers
import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory
curDir = "/home/meri/Documents/ISEF_2025/ISEF2025/patch_data.csv"
dataset = "/home/meri/SharedFolder/out"
dataframe = pd.read_csv(curDir)
listdir = os.listdir(dataset)
def trainVal_div(listdir):
    for f in listdir[0:int(len(listdir)/2)]:
        if (f.split("_")[5] == "tum.png.png"):
            shutil.move(dataset + "/" + f, "/home/meri/SharedFolder/train/cancerous/" + f)
        else:
            shutil.move(dataset + "/" + f, "/home/meri/SharedFolder/train/not_cancerous/" + f)
    for f in listdir[int(len(listdir)/2):]:
        if (f.split("_")[5] == "tum.png.png"):
            shutil.move(dataset + "/" + f, "/home/meri/SharedFolder/valid/cancerous/" + f)
        else:
            shutil.move(dataset + "/" + f, "/home/meri/SharedFolder/valid/not_cancerous/" + f)
#trainVal_div(listdir)
ds_train = image_dataset_from_directory(
       "/home/meri/SharedFolder/train",
       labels = 'inferred',
       label_mode = "binary",
       shuffle = "False"
)
ds_valid = image_dataset_from_directory(
    "/home/meri/SharedFolder/valid",
    labels = 'inferred',
    label_mode = "binary",
    shuffle = "False"
)

model = keras.Sequential([
    # First Convolutional Block
    layers.Conv2D(filters=32,
                  kernel_size=3,
                  strides = 1,
                  padding= 'same',
                  activation = 'relu'),
    layers.MaxPool2D(pool_size = 2,
                     strides = 1,
                     padding ='same'),
    
    # Second Convolutional Block
    layers.Conv2D(filters=64,
                  kernel_size=3,
                  strides = 1,
                  padding= 'same',
                  activation = 'relu'),
    layers.MaxPool2D(pool_size=2,
                     strides = 1,
                     padding ='same'),

    # Third Convolutional Block
    layers.Conv2D(filters=128,
                  kernel_size=3,
                  strides = 1,
                  padding= 'same',
                  activation = 'relu'),
    layers.MaxPool2D(pool_size=2,
                     strides = 1,
                     padding ='same'),

    # Classifier Head
    layers.Flatten(),
    layers.Dense(units=6, activation= 'relu'),
    layers.Dense(units=1, activation= 'sigmoid')

    ])

model.compile(
    optimizer=tf.keras.optimizers.Adam(epsilon=0.01),
    loss='binary_crossentropy',
    metrics=['binary_accuracy']
)

history = model.fit(
    ds_train,
    validation_data=ds_valid,
    epochs=40,
    verbose=0,
)

model.save("cancer_detection_model.h5")

history_frame = pd.DataFrame(history.history)
history_frame.loc[:, ['loss', 'val_loss']].plot()
history_frame.loc[:, ['binary_accuracy', 'val_binary_accuracy']].plot();
