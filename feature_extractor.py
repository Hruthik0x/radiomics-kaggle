import os
from radiomics import featureextractor, getFeatureClasses
from standardize import standardize, clean_up
import json
from sys import stdout 
import numpy as np 
import signal

# class TimeoutException(Exception):
#     pass

# def handle_timeout(signum, frame):
#     raise TimeoutException("The code took too long to execute and was aborted.")

# signal.signal(signal.SIGALRM, handle_timeout)

# def run_with_timeout(extractor, fol_path, timeout, fol, class_name):
#     signal.alarm(timeout)
#     try:
#         img_path = os.path.join(fol_path, "volume_resampled.nii.gz")
#         mask_path = os.path.join(fol_path, "labelmap_resampled.nii.gz")
#         try :
#             return extractor.execute(img_path, mask_path)
    
#         except Exception as e:
#             log(f"{fol} Error in {class_name}: {e}")
#             quit()

#     except TimeoutException:
#         return None
#     finally:
#         signal.alarm(0)

base_path = "/home/festus/Documents/pet-radiomics-challenges/Training_nifti/"
log_file = "/home/festus/Documents/GitHub/radiomics-kaggle/log_feture_extractor.txt"

# base_path = "/home/festus/Documents/pet-radiomics-challenges/Test_nifti/"
# log_file = "/home/festus/Documents/GitHub/radiomics-kaggle/log_feture_extractor_test.txt"

if os.path.exists(log_file) : 
    os.remove(log_file)

def log(string, eol = True) : 
    with open(log_file, "a+") as f:
        if eol : 
            f.write(string + "\n")
        else : 
            f.write(string)

def run_extractor(args):
    timeout = 300
    class_name, fol = args
    fol_path = os.path.join(base_path, fol)
    data_path = os.path.join(fol_path, class_name)
    extractor = featureextractor.RadiomicsFeatureExtractor()
    extractor.disableAllFeatures()
    extractor.enableFeaturesByName(**{class_name: []}) 

    img_path = os.path.join(fol_path, "volume_resampled.nii.gz")
    mask_path = os.path.join(fol_path, "labelmap_resampled.nii.gz")

    try : 
        # signal.alarm(timeout)
        features = extractor.execute(img_path, mask_path)
        # signal.alarm(0)
    except Exception as e:
        log (f"{fol} {class_name} : {e}")
        # signal.alarm(0)
        return 

    # filtered = {k: v for k, v in features.items() if not k.startswith("diagnostics_")}
    filtered = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in features.items() if not k.startswith("diagnostics_")}
    with open(data_path, 'w') as f:
        json.dump(filtered, f, indent=4)


def extract_features() : 
    classes = list(getFeatureClasses().keys())
    classes.pop(1)
    
    # Get the list of folders in the path
    folders = os.listdir(base_path)
    folders.sort()

    # Loop through each folder
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