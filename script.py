from os import mkdir, listdir, remove, path
from DICOMLib import DICOMUtils
import slicer 

# GLOBAL VARS

# log_file = "/home/festus/Documents/GitHub/radiomics-kaggle/log_training.txt"
# OUT_PATH = "/home/festus/Documents/pet-radiomics-challenges/Training_nifti/"
# db_dir = "/home/festus/Documents/pet-radiomics-challenges/Training/"

OUT_PATH = "/home/festus/Documents/pet-radiomics-challenges/Test_nifti/"
db_dir = "/home/festus/Documents/pet-radiomics-challenges/Test/"
log_file = "/home/festus/Documents/GitHub/radiomics-kaggle/log_test.txt"


def make_missing() :

    if not path.exists(OUT_PATH) :
        mkdir(OUT_PATH)

    if path.exists(log_file) :
        remove(log_file)

def log(string) : 

    with open(log_file, "a+") as f:
        f.write(string + "\n")

def dcm_to_nii() :
    patients = listdir(db_dir)
    patients.sort()
    max_ = len(patients)

    for i, patient in enumerate(patients):
        patient_dir = db_dir + patient
        loadedNodeIDs = []
        
        out_path = OUT_PATH + patient + "/"
        if not path.exists(out_path) :
            mkdir(out_path)

        with DICOMUtils.TemporaryDICOMDatabase() as db:
            DICOMUtils.importDicom(patient_dir, db)
            patientUIDs = db.patients()
            for patientUID in patientUIDs:
                try : 
                    loadedNodeIDs.extend(DICOMUtils.loadPatientByUID(patientUID))
                except : 
                    pass

        log(f"{i+1}/{max_} {patient} [{len(loadedNodeIDs)}] : {loadedNodeIDs}")

        if patient == "HN-MICCAI2018-0065" or patient == "HN-MICCAI2018-0066" : 
            segmentationNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSegmentationNode2")
        
        else : 
            segmentationNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSegmentationNode1")

        segmentation = segmentationNode.GetSegmentation()
        segmentID = segmentation.GetSegmentIdBySegmentName("GTVp")
        assert segmentID, f"GTVp segment not found in {patient}"
        labelmapNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
        
        segmentIDs = [segmentation.GetNthSegmentID(i) for i in range(segmentation.GetNumberOfSegments())]
        for segID in segmentIDs :
            if segID != segmentID :
                segmentation.RemoveSegment(segID)

        slicer.modules.segmentations.logic().ExportSegmentsToLabelmapNode(segmentationNode, [segmentID], labelmapNode)
        slicer.util.saveNode(labelmapNode, out_path + "labelmap.nii.gz" ) 

        transformNode = slicer.mrmlScene.GetNodeByID("vtkMRMLGridTransformNode1")
        volumeNode = slicer.mrmlScene.GetNodeByID("vtkMRMLScalarVolumeNode1")
        if transformNode :
            volumeNode.SetAndObserveTransformNodeID(transformNode.GetID())
            slicer.vtkSlicerTransformLogic().hardenTransform(volumeNode)
        slicer.util.saveNode(volumeNode, out_path+"volume.nii.gz")

        slicer.mrmlScene.Clear()

    # print(to_be_done)

if __name__ == "__main__" :
    make_missing()
    dcm_to_nii()
    exit(0)
