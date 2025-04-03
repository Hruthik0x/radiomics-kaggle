from os import mkdir, listdir, remove, path
from DICOMLib import DICOMUtils
import slicer 

db_dir = "/home/festus/Documents/pet-radiomics-challenges/Training/"
log_file = "/home/festus/Documents/GitHub/radiomics-kaggle/log.txt"
OUT_PATH = "/home/festus/Documents/GitHub/radiomics-kaggle/NIFTI/"

if not path.exists(OUT_PATH) :
    mkdir(OUT_PATH)

if path.exists(log_file) :
    remove(log_file)

def log(string) : 
    with open(log_file, "a+") as f:
        f.write(string + "\n")

    
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

    loadedNodeIDs = set(loadedNodeIDs)

    segmentationNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSegmentationNode1")
    assert segmentationNode, f"Segmentation node not found for {patient}"

    labelmapVolumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLLabelMapVolumeNode")
    volumeNode = slicer.mrmlScene.GetNodeByID("vtkMRMLScalarVolumeNode1")
    assert volumeNode, f"Volume node not found for {patient}"

    transformNode = slicer.mrmlScene.GetNodeByID("vtkMRMLGridTransformNode1")
    
    if len(loadedNodeIDs) == 4 :

        # uses vtkMRMLSegmentationNode1
        if patient == "HN-MICCAI2018-0064" : 
            pass 

        # uses vtkMRMLSegmentationNode2
        elif patient == "HN-MICCAI2018-0065" or patient == "HN-MICCAI2018-0066" : 
            segmentationNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSegmentationNode2")

        else : 
            assert False, f"Unexpected nodes: {loadedNodeIDs}"


    elif len(loadedNodeIDs) == 3 :
        assert loadedNodeIDs == {"vtkMRMLScalarVolumeNode1", "vtkMRMLSegmentationNode1", "vtkMRMLGridTransformNode1" }, f"Unexpected nodes: {loadedNodeIDs}"

    elif len(loadedNodeIDs) == 2 :
        assert loadedNodeIDs == {"vtkMRMLScalarVolumeNode1", "vtkMRMLSegmentationNode1" }, f"Unexpected nodes: {loadedNodeIDs}"

    else :
        assert False, f"Unexpected number of loaded nodes: {len(loadedNodeIDs)}"
    
    if transformNode : 
        volumeNode.SetAndObserveTransformNodeID(transformNode.GetID())
        slicer.vtkSlicerTransformLogic().hardenTransform(volumeNode)


    slicer.modules.segmentations.logic().ExportAllSegmentsToLabelmapNode(segmentationNode, labelmapVolumeNode)
    slicer.util.saveNode(labelmapVolumeNode, out_path + "labelmap.nii.gz" )
    slicer.util.saveNode(volumeNode, out_path+"volume.nii.gz")

    # cleanup
    slicer.mrmlScene.Clear()
