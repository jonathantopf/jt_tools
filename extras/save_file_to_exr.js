// This is a phoshop script to automoate saving exr textures from photoshop
// Its a total botch job but does the trick, procede with caution and if you do use it make sure to swap out the path of imf_copy to the correct one on your system

var imf_copy_path = "/Applications/Autodesk/maya2013/mentalray/bin/imf_copy";
var docName = activeDocument.path + "/" + activeDocument.name;
var intermediateDocName = docName.replace('PSD', 'tif').replace('psd', 'tif');
var finalDocName = intermediateDocName.replace('tif', 'exr')

var tiffSaveOptions = new TiffSaveOptions(); 
var intermediate = new File(docName);

activeDocument.saveAs(intermediate, tiffSaveOptions, true, Extension.LOWERCASE);

var convertCommand = new File(imf_copy_path + ' ' + intermediateDocName + ' ' + finalDocName);
convertCommand.execute();

var deleteIntermediateFileCommand = new File('rm ' + intermediateDocName);
deleteIntermediateFileCommand.execute();

alert(finalDocName);