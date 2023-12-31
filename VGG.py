# -*- coding: utf-8 -*-
"""VGG

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ho8iV2X-K0TZXJoSXdakpWDIBdGCnw63
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator

import numpy as np

from sklearn.metrics import precision_recall_fscore_support, accuracy_score,log_loss
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

import tensorflow as tf

class VGG16:
    def __init__(self, input_shape, num_classes):
        self.input_shape = input_shape
        self.num_classes = num_classes

    def build_model(self):
        tf.keras.backend.clear_session()
        inputs = tf.keras.Input(shape=self.input_shape)
        vgg16 = tf.keras.applications.VGG16(input_shape=self.input_shape,
                                            include_top=False,
                                            input_tensor=inputs,
                                            weights='imagenet')
        x = vgg16.get_layer('block5_conv3').output
        x = tf.keras.layers.GlobalAveragePooling2D()(x)
        outputs = tf.keras.layers.Dense(self.num_classes, activation='softmax')(x)
        model = tf.keras.Model(inputs, outputs)
        return model

# Creating an instance of the VGG16 class
vgg_model = VGG16(input_shape=(224, 224, 3), num_classes=1000)
model = vgg_model.build_model()

train_dir = "/content/drive/MyDrive/dataset/train"
test_dir = "/content/drive/MyDrive/dataset/train"
target_size = (128, 128)
batch_size = 10

train_datagen = ImageDataGenerator(rescale=1./255, validation_split = 0.15)
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest', validation_split = 0.15)

og_train_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=target_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset = 'training',
    shuffle=True
)

og_validation_data = train_datagen.flow_from_directory(
    train_dir,
    target_size=target_size,
    batch_size=1,
    class_mode='categorical',
    subset = 'validation',
    shuffle=True
)

aug_train_data = datagen.flow_from_directory(
    train_dir,
    target_size=target_size,
    batch_size=batch_size,
    class_mode='categorical',
    subset = 'training',
    shuffle=True
)

aug_validation_data = datagen.flow_from_directory(
    train_dir,
    target_size=target_size,
    batch_size=1,
    class_mode='categorical',
    subset = 'validation',
    shuffle = True
)

test_data = datagen.flow_from_directory(
    test_dir,
    target_size=target_size,
    batch_size=batch_size,
    class_mode="categorical",
    shuffle=False
)

def combine_gen(*gens):
  while True:
    for g in gens:
      yield next(g)
train_steps = (len(og_train_data)+len(aug_train_data)) // batch_size
validation_steps = (len(og_validation_data)+len(aug_validation_data)) // batch_size

model = VGG16(input_shape=(128,128,3), num_classes=4).build_model()
model.summary()

num_epochs = 8
optimizer = tf.keras.optimizers.Adam(0.0001)
model.compile(optimizer=optimizer, loss="categorical_crossentropy", metrics=["accuracy", tf.keras.metrics.Precision(), tf.keras.metrics.Recall()])

history = model.fit(combine_gen(og_train_data, aug_train_data),
                    steps_per_epoch=train_steps,
                    epochs=num_epochs,
                    validation_data= combine_gen(og_validation_data, aug_validation_data),
                    validation_steps = validation_steps,
          )

filename = "savedmodels/brain_tumor_VGG16.h5"
model.save(filename)

y_pred = model.predict(test_data)
y_pred_labels = tf.argmax(y_pred, axis=1)

y_true_labels = test_data.labels
y_pred_labels = y_pred_labels.numpy().tolist()
y_true_labels = y_true_labels.tolist()

precision, recall, f1_score, _ = precision_recall_fscore_support(y_true_labels, y_pred_labels)
cm = confusion_matrix(y_true_labels, y_pred_labels)
test_accuracy = accuracy_score(y_true_labels, y_pred_labels)
test_loss = log_loss(y_true_labels, y_pred)

print({
    "test_loss": test_loss,
    "test_precision": precision,
    "test_recall": recall,
    "test_f1_score": f1_score,
    "test_accuracy": test_accuracy})

display = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["atrofi","iskemi","normal","WMD"])
display.plot()

