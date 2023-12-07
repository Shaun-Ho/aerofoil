import pathlib as plib 
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import pathlib as plib
from datetime import datetime

current_file_path = plib.Path(__file__).parent
data_path = current_file_path.parents[1] / "data"
saved_models_path = current_file_path.parents[1] / "models"

def build_model(input_shape:tuple, norm: keras.layers.Normalization, outputs_list=list[str]) -> keras.Model:
    input_layer = keras.layers.Input(shape=input_shape)
    normalised_input = norm(input_layer)
    dense_layer = keras.layers.Dense(units=2, activation="relu", kernel_regularizer=keras.regularizers.l2(0.0001))(normalised_input)
    output_layer = keras.layers.Dense(units=1)(dense_layer)

    model = keras.Model(inputs=input_layer, outputs=output_layer)
    

    losses = dict()
    metrics = dict()
    for name in outputs_list:
        losses[name] = "mean_squared_error"
        metrics[name] = [tf.metrics.MeanAbsoluteError(), tf.metrics.RootMeanSquaredError(), tf.metrics.MeanAbsolutePercentageError()]

    model.compile(
        optimizer=keras.optimizers.Adam(
            learning_rate=.1,
        ),
        loss="mean_squared_error",
    )

    return model

def get_matching_colnames(df:pd.DataFrame, model_inputs:list[str], model_outputs:list[str]):
    # filtering outputs and outputs
    matching_inputs = []
    matching_outputs = []
    for i in model_inputs:
        matching_inputs.extend([colname for colname in df.columns if i.lower() in colname.lower()])
    for i in model_outputs:
        matching_outputs.extend([colname for colname in df.columns if i.lower() == colname.lower()])

    return matching_inputs, matching_outputs


def get_dataset(df:pd.DataFrame, matching_inputs:list[str], matching_outputs:list[str]):
    # splitting training and test set
    train_df = df.sample(frac=.8, random_state=0)
    test_df = df.drop(train_df.index)

    
    train_features = train_df[matching_inputs]
    test_features = test_df[matching_inputs]
    train_labels = train_df[matching_outputs]
    test_labels = test_df[matching_outputs]

    return train_features, train_labels, test_features, test_labels


def train_model(model_name:str,train_features, train_labels, **kwargs):
    callback_list = list()
    
    # Creating Normaliser
    normaliser = keras.layers.Normalization()
    normaliser.adapt(train_features)

    input_shape = (len(matching_inputs), )
    # build TF model
    model = build_model(input_shape, normaliser)

    model_iterations = list((saved_models_path / f"{model_name}").glob("*"))
    if len(model_iterations)>0:
        current_iteration = max([int(i.stem.split("_")[-1]) for i in model_iterations])
    else:
        current_iteration = 0

    callback_list.append(
        keras.callbacks.ModelCheckpoint(
        str(saved_models_path / f"{model_name}" / f"training_{current_iteration+1}" / "cp.ckpt"),
        save_weights_only=True,
        save_best_only=True
        )
    )

    history = model.fit(
        x=train_features,
        y=train_labels,
        epochs=100,
        validation_split=.2,
        callbacks=callback_list
    )

    return model
    
def evaluate_model(model:keras.Model, test_features:pd.DataFrame, test_labels:pd.DataFrame):
    model.evaluate(
        x=test_features,
        y=test_labels,
    )
    return

def predict_model(model:keras.Model):
    return




if __name__ == "__main__":
    file_name = "NACA0012"
    model_outputs = ["CL","CD","CM"]
    model_inputs = ["Cp"]

    model_name = "NACA0012"

    load_checkpoint = None
    save_checkpoint = True

    df = pd.read_csv(data_path / f"{file_name}.csv")
    matching_inputs, matching_outputs = get_matching_colnames(df, model_inputs, model_outputs)
    train_features, train_labels, test_features, test_labels = get_dataset(df, matching_inputs, matching_outputs)

    model = train_model(
        model_name=model_name,
        train_features=train_features,
        train_labels=train_labels
    )

    evaluate_model(model, test_features, test_labels)