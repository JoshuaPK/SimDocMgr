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
import subprocess
import sqlite3
import tempfile
import os
import shutil
import npyscreen

# Config Values:

scanpagePrg = '/usr/bin/scanimage'
scanpageOpts = '--format=TIFF --mode=Gray'

# Look here for opts:
# http://www.wizards-toolkit.org/discourse-server/viewtopic.php?t=23225

convertPrg = '/usr/bin/convert'
convertOpts = 'options'

dataDir = '../data'

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename='../log/simdocmgr.log', level=logging.INFO)

# Database Setup:

dbFile = dataDir + '/simdocmgr.db'
dbConn = sqlite3.connect(dbFile)
dbCur = dbConn.cursor()

# SQL Queries:

sqlLookupTags = 'SELECT tag_text FROM doc_tags WHERE tag_text LIKE ?'
sqlInsertNewTag = "INSERT INTO doc_tags (tag_text, create_date) VALUES (?, date('now'))"

# Code:

class TagSelector(npyscreen.wgautocomplete.Autocomplete):
    def auto_complete(self, input):

        global dbCur, dbConn, sqlLookupTags, sqlInsertNewTag

        # Is this tag in the database?

        locFldVal = self.value
        locResult = dbCur.execute(sqlLookupTags, [locFldVal, ])

        # If there are no results, add this to the database

        dbCur.execute(sqlInsertNewTag, [locFldVal, ])
        dbConn.commit()

        self.cursor_position=len(self.value)

        pass

class TitleTagSelector(npyscreen.wgtitlefield.TitleText):
    _entry_type = TagSelector

class SimDocApp(npyscreen.NPSApp):

    def main(self):

        MF = npyscreen.Form(name = "SIMple DOCument ManaGeR")
        fldTags = MF.add(TitleTagSelector, name = "Tags:", )
        fldAttribs = MF.add(npyscreen.TitleText, name = "Attributes:", )
        fldEffDt = MF.add(npyscreen.TitleDateCombo, name = "Effective Date:", )
        tagsList = MF.add(npyscreen.TitlePager, name = "Current Tags:", )

        MF.edit()

        pass



    def adjust_widgets(self):

        # This is called for every keypress


        pass
    
    def showError(errText):


        pass

    def waitForKey():


        pass

    def scanPages(nbrPages, outPath):

        """ Scans nbrPages pages and combines them into a PDF with a temporary file name,
            then puts the pdf in outPath """

        global scanpagePrg, scanpageOpts, convertPrg, convertOps

        tmpLoc = tempfile.mkdtemp(dir=dataDir)
        os.chdir(tmpLoc)

        for i in range(1, nbrPages):
            p = subprocess.Popen([scanpagePrg, scanpageOpts], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            spOut, spErr = p.communicate()
            tmpFP, tmpFN = tempfile.mkstemp(suffix='.tif',text=False)
            logging.info('Scanning page ' + str(i) + ' into file ' + tmpFN)
            os.write(tmpFP, spOut)
            os.close(tmpFP)
            logging.warning(spErr)
            p = None
            tmpFP = None
            tmpFN = None

            waitForKey() 

            pass

        # Now we use ImageMagick to glue all of the tiff files together into a pdf.

        logging.info("Gluing together PDF's")

        tmpFP, tmpFN = tempfile.mkstemp()
        os.close(tmpFP)
        tmpFN = tmpFN + '.pdf'
        logging.info("Created filename for PDF: " + tmpFN)

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

def displayUI():



    pass

def doStuff():

    #scanPages(2, 'test_loc')
    sdApp = SimDocApp()
    sdApp.run()

    pass

if __name__ == '__main__':


    doStuff()

    pass
