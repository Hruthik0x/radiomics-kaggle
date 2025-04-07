import os
from radiomics import featureextractor, getFeatureClasses
from standardize import standardize, clean_up
import json
from sys import stdout 
import numpy as np 

base_path = "/home/festus/Documents/pet-radiomics-challenges/Test_nifti/"
log_file = "/home/festus/Documents/GitHub/radiomics-kaggle/log_feture_extractor_test.txt"

if os.path.exists(log_file) : 
    os.remove(log_file)

def log(string, eol = True) : 
    with open(log_file, "a+") as f:
        if eol : 
            f.write(string + "\n")
        else : 
            f.write(string)

def run_extractor(args):
    class_name, fol = args
    fol_path = os.path.join(base_path, fol)
    data_path = os.path.join(fol_path, class_name)
    extractor = featureextractor.RadiomicsFeatureExtractor()
    extractor.disableAllFeatures()
    extractor.enableFeaturesByName(**{class_name: []}) 

    img_path = os.path.join(fol_path, "volume_resampled.nii.gz")
    mask_path = os.path.join(fol_path, "labelmap_resampled.nii.gz")

    try : 
        features = extractor.execute(img_path, mask_path)
    except Exception as e:
        log (f"{fol} {class_name} : {e}")
        return 

    filtered = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in features.items() if not k.startswith("diagnostics_")}
    with open(data_path, 'w') as f:
        json.dump(filtered, f, indent=4)


def extract_features() : 
    classes = list(getFeatureClasses().keys())
    classes.pop(1)
    
    folders = os.listdir(base_path)
    
    for i, folder in enumerate(folders) :
    
        fol_path = os.path.join(base_path, folder)
        proceed = False


        for a in classes:
            data_path = os.path.join(fol_path, a)
            if os.path.exists(data_path) : 
                continue 
            else : 
                proceed = True
                break

        if proceed : 

        # Check if fol_path has all 8 files 
        # if yes skip to next folder 
        # else standardize first 
        # skip feature extraction for features which are done 

            print(f"{i+1}   {folder} ", end= '')
            stdout.flush()

            standardize(fol_path)
            
            print(1, end = ' ')
            stdout.flush()

            for a in range(len(classes)):
                data_path = os.path.join(fol_path, classes[a])
                if os.path.exists(data_path) : 
                    print(a+2, end = ' ')
                    stdout.flush()
                    continue 
                else :
                    args = (classes[a], folder)
                    run_extractor(args)
                    print(a+2, end = ' ')
                    stdout.flush()
            print()
            clean_up(fol_path)

        else : 
            print(f"{i+1}   {folder} already done")

if __name__ == "__main__": 
    extract_features()