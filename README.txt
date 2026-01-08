=====================================================
  PDF FORENSIC SANITIZER
  Removes forensic traces from PDF files
=====================================================

WHAT THIS TOOL REMOVES:
-----------------------
  * Author name
  * Creator/Producer info
  * Creation/Modification timestamps
  * Timezone information (+02:00, etc.)
  * Hebrew language tags /Lang(he)
  * Document ID (UUID)
  * XMP Metadata
  * All traces inside compressed streams

HOW TO BUILD THE EXE:
---------------------
1. Make sure Python is installed on Windows
   Download from: https://www.python.org/downloads/

   IMPORTANT: Check "Add Python to PATH" during install!

2. Double-click: INSTALL_AND_BUILD.bat

3. Wait for the build to complete (1-2 minutes)

4. Find your EXE in the "dist" folder


HOW TO USE:
-----------
Option 1: Drag & Drop
  - Simply drag any PDF file onto PDF_Forensic_Sanitizer.exe

Option 2: GUI
  - Double-click the EXE to open file browser

Option 3: Command Line
  - PDF_Forensic_Sanitizer.exe yourfile.pdf


OUTPUT:
-------
The sanitized file will be saved as:
  yourfile_sanitized.pdf
(in the same folder as the original)


VERIFICATION:
-------------
After sanitizing, you can verify with:
  - ExifTool: exiftool sanitized.pdf
  - Online: https://www.metadata2go.com/


=====================================================
