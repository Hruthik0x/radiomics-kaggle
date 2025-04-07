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

    original_size = itk_image.GetSize()
    original_spacing = itk_image.GetSpacing()

    new_size = [
        int(round(original_size[0] * (original_spacing[0] / target_spacing[0]))),
        int(round(original_size[1] * (original_spacing[1] / target_spacing[1]))),
        int(round(original_size[2] * (original_spacing[2] / target_spacing[2]))),
    ]

    resampled_volume = sitk.Resample(
        itk_image, 
        new_size, 
        sitk.Transform(),
        sitk.sitkLinear,
        itk_image.GetOrigin(),
        target_spacing,
        itk_image.GetDirection(),
        0.0,
        itk_image.GetPixelID()
    )

    resampled_labelmap = sitk.Resample(
        labelmap_image, 
        new_size, 
        sitk.Transform(),
        sitk.sitkNearestNeighbor,
        itk_image.GetOrigin(),
        target_spacing,
        itk_image.GetDirection(),
        0.0,
        labelmap_image.GetPixelID()
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