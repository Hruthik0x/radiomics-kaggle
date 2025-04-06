import SimpleITK as sitk
from os import path 
import os


def standardize(fol_path) : 
    volume_path = path.join(fol_path, "volume.nii.gz")
    labelmap_path = path.join(fol_path, "labelmap.nii.gz")
    resampled_labelmap_path = path.join(fol_path, "labelmap_resampled.nii.gz")
    resampled_volume_path = path.join(fol_path, "volume_resampled.nii.gz")
    
    itk_image = sitk.ReadImage(volume_path)
    labelmap_image = sitk.ReadImage(labelmap_path)

    target_spacing = [1.0, 1.0, 1.0]

    # Get the original image size and spacing
    original_size = itk_image.GetSize()
    original_spacing = itk_image.GetSpacing()

    # Step 3: Calculate the new size based on the target spacing
    new_size = [
        int(round(original_size[0] * (original_spacing[0] / target_spacing[0]))),
        int(round(original_size[1] * (original_spacing[1] / target_spacing[1]))),
        int(round(original_size[2] * (original_spacing[2] / target_spacing[2]))),
    ]

    # import numpy as np
    # new_size = (np.round(original_size*(original_spacing/np.array(target_spacing)))).astype(int).tolist()

    # Step 4: Resample the volume image using the target size and spacing (linear interpolation for continuous data)
    resampled_volume = sitk.Resample(
        itk_image, 
        new_size, 
        sitk.Transform(),  # Identity transform (no rotation/translation)
        sitk.sitkLinear,   # Linear interpolation (for continuous volume data)
        itk_image.GetOrigin(),  # Keep the original origin
        target_spacing,    # Use the target spacing (1mm x 1mm x 1mm)
        itk_image.GetDirection(),  # Keep the original direction
        0.0,               # Background value (for padding)
        itk_image.GetPixelID()  # Use the original pixel type (e.g., int, float)
    )

    # Step 5: Resample the labelmap (segmentation mask) using nearest neighbor interpolation
    resampled_labelmap = sitk.Resample(
        labelmap_image, 
        new_size, 
        sitk.Transform(),  # Identity transform (no rotation/translation)
        sitk.sitkNearestNeighbor,  # Nearest neighbor interpolation (for labels/segmentation)
        itk_image.GetOrigin(),  # Keep the original origin
        target_spacing,  # Use the target spacing (1mm x 1mm x 1mm)
        itk_image.GetDirection(),  # Keep the original direction
        0.0,  # Background value (for padding)
        labelmap_image.GetPixelID()  # Use the original pixel type (e.g., int)
    )

    # Save the resampled images
    sitk.WriteImage(resampled_volume, resampled_volume_path)
    sitk.WriteImage(resampled_labelmap, resampled_labelmap_path)

def clean_up(fol_path) : 
    resampled_labelmap_path = path.join(fol_path, "labelmap_resampled.nii.gz")
    resampled_volume_path = path.join(fol_path, "volume_resampled.nii.gz")
    
    try : 
        # Remove the original files
        os.remove(resampled_labelmap_path)
        os.remove(resampled_volume_path)
    except : 
        pass