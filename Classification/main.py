import numpy as np
import tensorflow as tf
from tensorflow.keras.layers import Input, LeakyReLU, Concatenate, Activation, BatchNormalization, Bidirectional, LSTM, Dense, Dropout, Conv1D, MaxPooling1D, Flatten, Embedding
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import Model
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier
import pandas as pd
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
import subprocess
from subprocess import Popen
import joblib
import optuna
import numpy as np
import seqdata
import argparse
import warnings
from Bio import SeqIO
import os, shutil
from tqdm import tqdm

def conventional_models(algorithm, train_data, test_data):
    X_train, y_train = train_data[0].features, np.argmax(train_data[0].labels, axis=1)
    X_test, y_test = test_data[0].features, np.argmax(test_data[0].labels, axis=1)

    def objective(trial):
        
        if algorithm == 0:
            params = {
                'C': trial.suggest_loguniform('C', 1e-4, 1e2),
                'gamma': trial.suggest_loguniform('gamma', 1e-4, 1e2),
            }

            model = make_pipeline(StandardScaler(), SVC(**params, kernel = 'rbf', probability = True, random_state = SEED))
        elif algorithm == 1:
            params = {
                'max_depth': trial.suggest_int('max_depth', 1, 9),
                'learning_rate': trial.suggest_loguniform('learning_rate', 0.01, 1.0),
                'n_estimators': trial.suggest_int('n_estimators', 50, 500),
                'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
                'gamma': trial.suggest_loguniform('gamma', 1e-8, 1.0),
                'subsample': trial.suggest_loguniform('subsample', 0.01, 1.0),
                'colsample_bytree': trial.suggest_loguniform('colsample_bytree', 0.01, 1.0),
                'reg_alpha': trial.suggest_loguniform('reg_alpha', 1e-8, 1.0),
                'reg_lambda': trial.suggest_loguniform('reg_lambda', 1e-8, 1.0),
                'eval_metric': 'mlogloss',
                'use_label_encoder': False
            }

            model = make_pipeline(StandardScaler(), XGBClassifier(**params, random_state=SEED))

        scores = cross_val_score(model, X_train, y_train, n_jobs=-1, cv=10, scoring='precision_weighted')
        weighted_precision = scores.mean()

        return weighted_precision

    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED))
    study.optimize(objective, n_trials=100)
    print(study.best_trial)

    if algorithm == 0:
        model = make_pipeline(StandardScaler(), SVC(**study.best_trial.params, kernel = 'rbf', probability = True, random_state = SEED))
    elif algorithm == 1:
        model = make_pipeline(StandardScaler(), XGBClassifier(**study.best_trial.params, random_state=SEED))

    model.fit(X_train, y_train)
    model_pred = model.predict(X_test)

    report = classification_report(y_test, model_pred, target_names=test_data[0].names, output_dict=True)

    df_report = pd.DataFrame(report).T

    df_report.to_csv(f'{output_folder}/results.csv')
    
def load_data(train_path, test_path, encoding, feat_extraction, k, path_model, features_exist):
    train_data, test_data, max_len = [], [], []

    for enc in range(2):
        if enc == encoding or encoding >= 2: # specific encoding or all encodings
            train, test = seqdata.Seq(train_path, enc, k), seqdata.Seq(test_path, enc, k)
            enc_length = seqdata.pad_data(train, test)

            train_data.append(train)
            test_data.append(test)
            max_len.append(enc_length)

    if feat_extraction or encoding == 2:
        train_fasta, train_labels = train_data[0].fastas, train_data[0].names
        test_fasta, test_labels = test_data[0].fastas, test_data[0].names

        if not features_exist:
            print('Using Feature Engineering from BioAutoML...')
            subprocess.run(['python', 'BioAutoML-feature.py', '--fasta_train'] + train_fasta + ['--fasta_label_train'] + train_labels +
                            ['--fasta_test'] + test_fasta + ['--fasta_label_test'] + test_labels + ['--output', 'bioautoml-results'])
        
            subprocess.run(['cp', 'bioautoml-results/best_descriptors/best_train.csv', 'features/best_train.csv'])
            subprocess.run(['cp', 'bioautoml-results/best_descriptors/best_test.csv', 'features/best_test.csv'])

        train_data[0].features = pd.read_csv("features/best_train.csv").values.astype(np.float32)
        test_data[0].features = pd.read_csv("features/best_test.csv").values.astype(np.float32)

        max_len.append(train_data[0].features.shape[1])

    return train_data, test_data, max_len

def load_data_predict(test_path, encoding, feat_extraction, k, scaler):
    train_data = joblib.load('features/train_data.pkl')

    predict_path = os.path.join(test_path, "predict.fasta")

    test_data = []

    for enc in range(2):
        if enc == encoding or encoding >= 2: # specific encoding or all encodings
            test = seqdata.Seq(test_path, enc, k)

            test_data.append(test)

    for train, test in zip(train_data, test_data):
        seqdata.pad_data(train, test)

    df_predict, nameseqs = test_extraction(test_data)

    test_data[0].features = df_predict

    predict_sequences(model, encoding, nameseqs, train_data, test_data, feat_extraction, scaler, f'{output_folder}/model_predictions.csv')

def conv_block(x, conv_params):
    for _ in range(conv_params['num_convs']):
        x = Conv1D(filters=128, kernel_size=3, padding='same')(x)
        if conv_params['batch_norm']:
            x = BatchNormalization()(x)

        x = Activation(LeakyReLU())(x) if conv_params['activation'] else Activation('relu')(x)

        x = MaxPooling1D(pool_size=2)(x)

        if conv_params['dropout'] > 0:
            x = Dropout(conv_params['dropout'])(x)

    return x

def lstm_block(x, lstm_params):
    for i in range(lstm_params['num_lstm']):
        
        seq = True if lstm_params['num_lstm'] > 1 and i < lstm_params['num_lstm'] - 1 else False

        if lstm_params['bidirectional']:
            x = Bidirectional(LSTM(128, return_sequences=seq))(x)
        else:
            x = LSTM(128, return_sequences=seq)(x)

        if lstm_params['dropout'] > 0:
            x = Dropout(lstm_params['dropout'])(x)

    return x

def base_layers(encoding, concat, max_len, k, conv_params, lstm_params):
    num_combs = 4 ** k

    if encoding == 0: # One-hot encoding
        input_layer = Input(shape=(max_len, num_combs))

        x = conv_block(input_layer, conv_params)

        x = lstm_block(x, lstm_params)

        if concat == 1:
            out = Flatten()(x)
        elif concat == 2:
            x = Flatten()(x)
            x = Dense(128, activation='relu')(x)
            out = Dropout(0.5)(x)
    elif encoding == 1: # K-mer embedding
        input_layer = Input(shape=(max_len,))

        x = Embedding(num_combs, 128, input_length=max_len)(input_layer)

        x = conv_block(x, conv_params)

        x = lstm_block(x, lstm_params)

        if concat == 1:
            out = Flatten()(x)
        elif concat == 2:
            x = Flatten()(x)
            x = Dense(128, activation='relu')(x)
            out = Dropout(0.5)(x)
    elif encoding == 2: # no encoding
        input_layer = Input(shape=(max_len,))

        if concat == 1:
            out = Flatten()(input_layer)
        elif concat == 2:
            x = Flatten()(input_layer)
            x = Dense(128, activation='relu')(x)
            out = Dropout(0.5)(x)

    return input_layer, out

def create_model(encoding, concat, feat_extraction, num_labels, max_len, k, conv_params, lstm_params):
    input_layers, outs = [], []

    for enc in range(2):

        if enc == encoding or encoding == 3: # specific encoding or all encodings

            if encoding == 3:
                in_layer, x = base_layers(enc, concat, max_len[enc], k, conv_params, lstm_params)
            else:
                in_layer, x = base_layers(enc, concat, max_len[0], k, conv_params, lstm_params)
            
            input_layers.append(in_layer)
            outs.append(x)

    if encoding == 2 or feat_extraction:
        in_layer, x = base_layers(2, concat, max_len[-1], k, conv_params, lstm_params)
        input_layers.append(in_layer)
        outs.append(x)

    if encoding == 3 or (encoding < 2 and feat_extraction):
        outs = Concatenate()(outs)
    else:
        outs = outs[0]

    # Dense layers
    if concat == 1:
        x = Dense(128, activation='relu')(outs)
        x = Dropout(0.5)(x)
        x = Dense(64, activation='relu')(x)
    elif concat == 2:
        x = Dense(64, activation='relu')(outs)
    
    x = Dropout(0.5)(x)
    output_layer = Dense(num_labels, activation='softmax')(x)

    model = Model(inputs=input_layers, outputs=output_layer)

    model.compile(loss='categorical_crossentropy', optimizer= tf.keras.optimizers.Adam(learning_rate=1e-4),
                    metrics= [tf.keras.metrics.Precision(name="precision")])

    model.summary()

    return model

def train_model(model, encoding, train_data, feat_extraction, epochs, patience, scaling, output_folder):
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=patience, restore_best_weights=True, verbose=1)
    ]

    X_train, X_test, y_train, y_test = [], [], [], []

    if encoding == 2:
        feature_X_train, feature_X_test, feature_y_train, feature_y_test = train_test_split(train_data[0].features, train_data[0].labels, test_size=0.1, shuffle=True, stratify=train_data[0].labels, random_state=SEED)

        X_train.append(feature_X_train)
        X_test.append(feature_X_test)
        y_train.append(feature_y_train)
        y_test.append(feature_y_test)
    else:
        features = [train.seqs for train in train_data]

        if feat_extraction:
            features.append(train_data[0].features)

        for feature in features:
            feature_X_train, feature_X_test, feature_y_train, feature_y_test = train_test_split(feature, train_data[0].labels, test_size=0.1, shuffle=True, stratify=train_data[0].labels, random_state=SEED)
            
            X_train.append(feature_X_train)
            X_test.append(feature_X_test)
            y_train.append(feature_y_train)
            y_test.append(feature_y_test)

    if feat_extraction:
        X_train[-1] = scaling.fit_transform(X_train[-1])
        X_test[-1] = scaling.transform(X_test[-1])
        joblib.dump(scaler, "features/scaler.pkl")

    model.fit(X_train, y_train, validation_data=(X_test, y_test), batch_size=32, epochs=epochs, shuffle=True, callbacks=callbacks)

    model.save(f"{output_folder}/model.h5")

def report_model(model, encoding, test_data, feat_extraction, scaling, output_file):
    if encoding == 2:
        features = scaling.transform(test_data[0].features)
    else:
        features = [test.seqs for test in test_data]

        if feat_extraction:
            features.append(scaling.transform(test_data[0].features))

    model_pred = model.predict(features)
    y_pred = np.argmax(model_pred, axis=1)
    y_true = np.argmax(test_data[0].labels, axis=1)

    report = classification_report(y_true, y_pred, target_names=train_data[0].names, output_dict=True)
    
    df_report = pd.DataFrame(report).T

    df_report.to_csv(output_file)

def test_extraction(test_data):
    datasets = []

    path = 'features/feat_extraction'

    try:
        shutil.rmtree(path)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
        print('Creating Directory...')

    if not os.path.exists(path):
        os.mkdir(path)

    datasets.append(path + '/kGap_di.csv')
    datasets.append(path + '/kGap_tri.csv')
    datasets.append(path + '/ORF.csv')
    datasets.append(path + '/Fickett.csv')
    datasets.append(path + '/FourierBinary.csv')
    datasets.append(path + '/Tsallis.csv')
    datasets.append(path + '/repDNA.csv')

    commands = [['python', 'MathFeature/methods/Kgap.py', '-i',
                        test_data[0].fastas[0], '-o', path + '/kGap_di.csv', '-l',
                        'predict', '-k', '1', '-bef', '1',
                        '-aft', '2', '-seq', '1'],
                ['python', 'MathFeature/methods/Kgap.py', '-i',
                        test_data[0].fastas[0], '-o', path + '/kGap_tri.csv', '-l',
                        'predict', '-k', '1', '-bef', '1',
                        '-aft', '3', '-seq', '1'],
                ['python', 'MathFeature/methods/CodingClass.py', '-i',
                        test_data[0].fastas[0], '-o', path + '/ORF.csv', '-l', 'predict'],
                ['python', 'MathFeature/methods/FickettScore.py', '-i',
                        test_data[0].fastas[0], '-o', path + '/Fickett.csv', '-l', 'predict',
                        '-seq', '1'],
                ['python', 'MathFeature/methods/FourierClass.py', '-i',
                        test_data[0].fastas[0], '-o', path + '/FourierBinary.csv', '-l', 'predict',
                        '-r', '1'],
                ['python', 'other-methods/TsallisEntropy.py', '-i',
                        test_data[0].fastas[0], '-o', path + '/Tsallis.csv', '-l', 'predict',
                        '-k', '5', '-q', '2.3'],
                ['python', 'other-methods/repDNA/repDNA-feat.py', '--file',
                        test_data[0].fastas[0], '--output', path + '/repDNA.csv', '--label', 'predict']
    ]

    processes = [Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) for cmd in commands]
    for p in processes: p.wait()

    if datasets:
        datasets = list(dict.fromkeys(datasets))
        dataframes = pd.concat([pd.read_csv(f) for f in datasets], axis=1)
        dataframes = dataframes.loc[:, ~dataframes.columns.duplicated()]
        dataframes = dataframes[~dataframes.nameseq.str.contains("nameseq")]

    dataframes.pop('label')
    nameseqs = dataframes.pop('nameseq')

    df_train = pd.read_csv("features/best_train.csv")

    common_columns = dataframes.columns.intersection(df_train.columns)
    df_predict = dataframes[common_columns]

    return df_predict, nameseqs

def predict_sequences(model, encoding, nameseqs, train_data, test_data, feat_extraction, scaling, output):
    if encoding == 2:
        features = scaling.transform(test_data[0].features)
    else:
        features = [test.seqs for test in test_data]

        if feat_extraction:
            features.append(scaling.transform(test_data[0].features))

    model_pred = model.predict(features)

    df_predicted = pd.DataFrame(model_pred, columns=train_data[0].names)

    sequences = []

    for record in SeqIO.parse(test_data[0].fastas[0], "fasta"):
        sequences.append(str(record.seq))

    seqs = pd.DataFrame({
        'sequence': sequences
    })

    df_predicted = pd.concat([nameseqs, seqs, df_predicted], axis=1)

    df_predicted['prediction'] = [train_data[0].names[index] for index in np.argmax(model_pred, axis=1)]

    df_predicted.to_csv(output, index=False)

# Best configuration example
# python main.py --train data/train/ --test data/predict/ --path_model results/enc1_cnn_bilstm_4conv_k1_concat2_bio/model.h5 --encoding 1 --k 1 --concat, 2 --feat_extraction 1 --features_exist 1 --output data/predict/results_right/

if __name__ == '__main__':
    warnings.filterwarnings(action='ignore', category=FutureWarning)
    warnings.filterwarnings('ignore')
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    os.chdir("../Classification")

    SEED = 0
    tf.keras.utils.set_random_seed(SEED)  # sets seeds for base-python, numpy and tf
    tf.config.experimental.enable_op_determinism()

    parser = argparse.ArgumentParser()
    parser.add_argument('-train', '--train', help='Folder with FASTA training files')
    parser.add_argument('-test', '--test', help='Folder with FASTA testing files')
    parser.add_argument('-epochs', '--epochs', default=10, help='Number of epochs to train')
    parser.add_argument('-patience', '--patience', default=10, help='Epochs to stop training after loss plateau')
    parser.add_argument('-encoding', '--encoding', default=0, help='Encoding - 0: One-hot encoding, 1: K-mer embedding, 2: No encoding (only feature extraction), 3: All encodings (without feature extraction)')
    parser.add_argument('-k', '--k', default=1, help='Length of k-mers')
    parser.add_argument('-concat', '--concat', default=1, help='Concatenation type - 1: Directly, 2: Using dense layer before concatenation')
    
    # Run BioAutoML
    parser.add_argument('-feat_extraction', '--feat_extraction', default=0, help='Feature engineering using BioAutoML - 0: False, 1: True; Default: False')
    
    parser.add_argument('-features_exist', '--features_exist', default=0, help='If features exists - 0: False, 1: True; Default: True')
    # Choose between conventional and deep learning algorithms
    parser.add_argument('-algorithm', '--algorithm', default=2, help='Algorithm - 0: Support Vector Machines (SVM), 1: Extreme Gradient Boosting (XGBoost), 2: Deep Learning')

    # CNN parameters
    parser.add_argument('-num_convs', '--num_convs', default=1, help='Number of convolutional layers')
    parser.add_argument('-activation', '--activation', default=0, help='Activation to use - 0: ReLU, 1: Leaky ReLU; Default: ReLU')
    parser.add_argument('-batch_norm', '--batch_norm', default=0, help='Use Batch Normalization for Convolutional Layers - 0: False, 1: True; Default: False')
    parser.add_argument('-cnn_dropout', '--cnn_dropout', default=0, help='Dropout rate between Convolutional layers - 0 to 1')

    # LSTM parameters
    parser.add_argument('-num_lstm', '--num_lstm', default=1, help='Number of LSTM layers')
    parser.add_argument('-bidirectional', '--bidirectional', default=0, help='Use Bidirectional LSTM - 0: False, 1: True; Default: False')
    parser.add_argument('-lstm_dropout', '--lstm_dropout', default=0, help='Dropout rate between LSTM layers - 0 to 1')

    # Output folder
    parser.add_argument('-output', '--output', default=0, help='Output folder for classification reports.')

    # Load saved model
    parser.add_argument('-path_model', '--path_model', help='Path to load saved model')
    
    args = parser.parse_args()

    train_path = args.train
    test_path = args.test

    algorithm = int(args.algorithm)
    epochs = int(args.epochs)
    patience = int(args.patience)
    encoding = int(args.encoding)
    k = int(args.k)
    concat = int(args.concat)

    feat_extraction = int(args.feat_extraction)
    
    output_folder = args.output

    path_model = args.path_model
    features_exist = int(args.features_exist)

    conv_params = {'num_convs': int(args.num_convs), 'activation': int(args.activation), 'batch_norm': int(args.batch_norm) , 'dropout': float(args.cnn_dropout)}

    lstm_params = {'num_lstm': int(args.num_lstm), 'bidirectional': int(args.bidirectional), 'dropout': float(args.lstm_dropout)}

    print(f"Working directory: {os.getcwd()}")
    print(f"FASTA directory: {test_path}")

    # folder for model
    if not features_exist:
        path = 'features'

        try:
            shutil.rmtree(path)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
            print('Creating Directory...')

        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    os.makedirs(output_folder, exist_ok=True)

    if algorithm == 2:

        scaler = StandardScaler()

        if path_model:
            model = tf.keras.models.load_model(path_model)

            if feat_extraction:
                scaler = joblib.load('features/scaler.pkl')

            load_data_predict(test_path, encoding, feat_extraction, k, scaler)
        else:
            train_data, test_data, max_len = load_data(train_path, test_path, encoding, feat_extraction, k, path_model, features_exist)

            num_labels = len(train_data[0].names)

            model = create_model(encoding, concat, feat_extraction, num_labels, max_len, k, conv_params, lstm_params)

            train_model(model, encoding, train_data, feat_extraction, epochs, patience, scaler, output_folder)

            report_model(model, encoding, test_data, feat_extraction, scaler, f'{output_folder}/results.csv')

        tf.keras.utils.plot_model(
            model,
            to_file= f'{output_folder}/model.png',
            show_shapes=False,
            show_dtype=False,
            show_layer_names=True,
            rankdir='TB',
            expand_nested=False,
            dpi=96,
            layer_range=None,
            show_layer_activations=False
        )
        
    else:
        train_data, test_data, max_len = load_data(train_path, test_path, encoding, feat_extraction, k, path_model, features_exist)

        conventional_models(algorithm, train_data, test_data)