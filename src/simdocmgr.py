#!/usr/bin/python

# Simple DOCument ManaGeR
# Copyright 2016 Joshua Kramer

# Process Flow:

# To import existing PDF's into the database (must be in page order!)

# simdocmgr -f pdf_file.pdf -a attribute:value -t tag1 tag2 tag3

# For example:
# simdocmgr -f pdf_file.pdf -a company:Centurylink -t bill phone internet

# To scan documents interactively:

# simdocmgr

# Then enter the number of pages, attribute:value pairs, and tags

import logging
import urwid
import subprocess
import sqlite3
import tempfile
import os
import shutil

# Config Values:

scanpagePrg = '/usr/bin/scanpage'
scanpageOpts = 'options'

convertPrg = '/usr/bin/convert'
convertOpts = 'options'

dataDir = '../data'

# Code:

def scanPages(nbrPages, outPath):

    """ Scans nbrPages pages and combines them into a PDF with a temporary file name,
        then puts the pdf in outPath """

    global scanpagePrg, scanpageOpts, convertPrg, convertOps

    tmpLoc = tempfile.mkdtemp(dir=dataDir)
    os.chdir(tmpLoc)

    for i in range(1, nbrPages):
        p = subprocess.Popen([scanpagePrg, scanpageOpts], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        spOut, spErr = p.communicate()
        logging.info("Logging page " + str(i))
        logging.info(spOut)
        logging.warning(spErr)
        p = None

    # Now we use ImageMagick to glue all of the tiff files together into a pdf.

    logging.info("Gluing together PDF's")

    tmpFP, tmpFN = tempfile.mkstmp()
    tmpFP.close()
    tmpFN = tmpFN + '.pdf'
    logging.info("Created filename: " tmpFN)

    p = subprocess.Popen([convertPrg, convertOpts], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cvOut, cvErr = p.communicate()
    p = None

    logging.info(cvOut)
    logging.warning(cvErr)

    # Now we should have a PDF in the data directory, if things worked as planned.
    # Build the cpString- the command to copy the file to its final location.

    cpString = tmpFN + ' ../' + outPath
    logging.info("Copying file using args: " + cpString)

    p = subprocess.Popen(['/usr/bin/cp', cpString], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cpOut, cpErr = p.communicate()
    p = None

    logging.info(cpOut)
    logging.warning(cpErr)

    # Now, remove the temp directory.
    os.chdir('..')
    shutil.rmtree(tmpLoc)

    # All done!

    pass


def doStuff():

    scanPages(2, 'test_loc')

    pass

if __name__ == '__main__':


    doStuff()

    pass
