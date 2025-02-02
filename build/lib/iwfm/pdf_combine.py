# pdf_combine.py
# Combines all of the PDF files in a folder into one PDF file
# info and gwhyd_sim columns, and returns the dictionary
# Copyright (C) 2020-2021 University of California
# -----------------------------------------------------------------------------
# This information is free; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This work is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
# -----------------------------------------------------------------------------


def pdf_combine(start_dir, save_dir, save_name):
    ''' PDF_combine() - Combine all of the PDF files in a folder into one PDF file
    modified from https://geektechstuff.com/2018/02/17/python-3-merge-multiple-pdfs-into-one-pdf/

    Parameters
    ----------
    start_dir : str
        Name directory with PDF files to combine

    save_dir : str
        Name of output directory

    save_name : str
        Name of output file

    Returns
    -------
    count : int
        Number of PDFs combined

    '''
    import os, PyPDF2

    os.chdir(save_dir)  # change to PDFs folder
    count = 0
    mergelist = []
    for filename in os.listdir('.'):
        if filename.endswith('.pdf'):
            mergelist.append(filename)

    pdfWriter = PyPDF2.PdfFileWriter()

    # loop through all PDFs
    for filename in mergelist:
        count += 1
        pdfFileObj = open(filename, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        for pageNum in range(pdfReader.numPages):  
            pageObj = pdfReader.getPage(pageNum)
            pdfWriter.addPage(pageObj)

    os.chdir(start_dir) 
    pdfOutput = open(save_name, 'wb') 
    pdfWriter.write(pdfOutput) 
    pdfOutput.close()  
    return count
