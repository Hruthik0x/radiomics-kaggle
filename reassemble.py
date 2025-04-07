from os import listdir, path
import pandas
from radiomics import getFeatureClasses
import json

base_path = "/home/festus/Documents/pet-radiomics-challenges/Test_nifti/"
out_path = "/home/festus/Documents/pet-radiomics-challenges/Test_features.csv"
in_path = "/home/festus/Documents/pet-radiomics-challenges/Test.csv"

def assemble() : 	
    df = pandas.read_csv(in_path)
    df.set_index("Subject_ID", inplace=True)


    classes = list(getFeatureClasses().keys())
    classes.pop(1)
	
    folders = listdir(base_path)
    folders.sort()
	
    for fol in folders : 
        fol_path = path.join(base_path, fol)
        data = {}
        for class_ in classes : 
            class_path = path.join(fol_path, class_)
            data.update(json.loads(open(class_path).read()))

        for key, val in data.items() :
            df.at[fol, key] = val

    df.reset_index(inplace=True)
    df.to_csv(out_path, index = False)

if __name__ == "__main__" : 
	assemble()
