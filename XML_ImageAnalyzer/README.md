# XMLImageAnalyzer
MATLAB program which roughly estimates the number of images taken and their combined size from an XML timeline. Useful in approxmating the date useage. MATLAB is used because could not find Python packages that handles 12 bit jpeg images.

XMLImageAnalyzer goes through an XML, line by line, and estimates the amount of Images
taken and their combined size.

Run Main_XML_ImageAnalyzer in MATLAB. If problems occur try using at least MATLAB 2018.

An atmospheric and gravitation wave model creates a single limb radiance matrix which is used 
to estimate the values of the CCDs whenever JPEG compression is applied.
Note that only a single scene is generated for the CCDs, and is only applicable to
pointing altitude of about 92500 km, meaning that
JPEG compression estimation for other pointing altitudes and the nadir CCD is not accurate.
The same scene is though still used to estimate JPEG compression for pointing
altitudes up to 120 km. For other pointing altitudes and the nadir CCD a
matrix just containing noise is used instead.
