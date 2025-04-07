### rtstruct_to_nifti
- Utilized the 3D Slicer API to convert RTSTRUCT DICOM files into NIfTI format, making them compatible with libraries that require NIfTI input.

- Filtered the segmentation/labelmap to retain only the tumor region, removing all other structures.

- Saved both the processed labelmap (segmentation) and the corresponding anatomical volume as separate NIfTI files for further processing.

### feature_extractor
- Resampled both the volume and the tumor labelmap to a uniform voxel spacing of 1mm x 1mm x 1mm, ensuring consistency across all patient data.

- Applied zero-padding to the labelmap to match the dimensions of the resampled volume.

- Extracted radiomic features using PyRadiomics `'firstorder', 'gldm', 'glrlm', 'glszm', 'ngtdm', 'shape', 'shape2D'`

- Saved the extracted features for each patient in individual files (7 json files per patient, 1 json per each class of features).

### reassemble
- Loaded the individual feature files for all patients and consolidated them into a single CSV file.

- Merged associated clinical data (e.g., age, sex, T/N-category, p16 status) with the radiomic features to create a complete training dataset.

### xgboost
- Trained machine learning models using the XGBoost framework with the 'hist' tree method for optimized performance on structured data.

- Trrained three model for the 3 different cases given in the Test nifti
    - Case 1 : No value is missing
    - Case 2 : AJCC 7th edition data is missing
    - Case 3 : AJCC 7th edition, AJCC 8th edition and N type data is missing

- Assigned each model to handle their respective cases
- Combined the output from each model into a single csv file