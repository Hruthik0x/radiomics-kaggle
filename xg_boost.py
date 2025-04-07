import pandas as pd
from os import path
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

train_path = "/home/festus/Documents/pet-radiomics-challenges/Training_features.csv"
test_path = "/home/festus/Documents/pet-radiomics-challenges/Test_features.csv"
base_path = "/home/festus/Documents/pet-radiomics-challenges/"

def train_model(model, X, y, split = 0) :

    if split == 0.0 : return model.fit(X, y)

    else :

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=split, random_state=26123)

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {accuracy:.4f}")

        return model.fit(X, y)


def gen_models(split = 0) :

    df = pd.read_csv(train_path).dropna()
    models = []

        
    categories = ["Sex", 'p16_expression', 'T_category', 'N_category',
                'AJCC_7th_edition', 'AJCC_8th_edition', 'Vital_status']
    
    for categ in categories : 
        df[categ] = df[categ].astype('category')
    
    for _ in range(3) :
        models.append(xgb.XGBClassifier(
            enable_categorical=True,
            eval_metric='logloss',
            tree_method='hist'
            ))

    y = df['Local_control']

    # when all vals are present 
    X = df.drop(['Subject_ID', 'Local_control'], axis=1)
    models.append(train_model(models.pop(0), X, y, split))
    
    # when AJCC_7th edition is missing 
    X.drop(['AJCC_7th_edition'], axis=1, inplace=True)
    models.append(train_model(models.pop(0), X, y, split))

    # when N_category, AJCC_7th edition, AJCC_8th edition are missing
    X.drop(['N_category', 'AJCC_8th_edition'], axis=1, inplace=True)
    models.append(train_model(models.pop(0), X, y, split))

    return models

def test(split = 0) :
    
    models = gen_models(split)
    df = pd.read_csv(test_path).drop(['Local_control'], axis=1)

    categories = ["Sex", 'p16_expression', 'T_category', 'N_category',
                    'AJCC_7th_edition', 'AJCC_8th_edition', 'Vital_status']
    for categ in categories:
        df[categ] = df[categ].astype('category')

    missing_1 = df.copy()[df["AJCC_7th_edition"].isna() & df.drop(columns=["AJCC_7th_edition"]).notna().all(axis=1)]
    missing_1.drop(['AJCC_7th_edition'], axis=1, inplace=True)

    missing_3 = df.copy()[df[['N_category', 'AJCC_7th_edition', 'AJCC_8th_edition']].isna().all(axis=1)]
    missing_3.drop(['N_category', 'AJCC_7th_edition', 'AJCC_8th_edition'], axis=1, inplace=True)

    all_present = df.dropna()

    df = pd.read_csv(path.join(base_path , "Test.csv"))
    df = df[['Subject_ID', 'Local_control']]
    
    df.set_index("Subject_ID", inplace=True)

    predict(models[2], missing_3,  df)
    predict(models[1], missing_1,  df)
    predict(models[0], all_present, df)

    df.reset_index(inplace=True)
    df.to_csv(path.join(base_path, f"submission.csv"), index=False, float_format="%.0f")


def predict(model, X_test, df) :
    ids = X_test["Subject_ID"].tolist()

    X_test = X_test.drop(['Subject_ID'], axis=1)
    y_pred = model.predict(X_test)

    for patient_id, prediction in zip(ids, y_pred):
        df.at[patient_id, 'Local_control'] = prediction

    return df


if __name__ == "__main__" : 
    test()