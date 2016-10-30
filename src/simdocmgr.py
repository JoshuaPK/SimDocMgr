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

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename='../log/simdocmgr.log', level=logging.DEBUG)

# Database Setup:

dbFile = dataDir + '/simdocmgr.db'
dbConn = sqlite3.connect(dbFile)
dbCur = dbConn.cursor()

# SQL Queries:

sqlLookupTags = "SELECT tag_text FROM doc_tags WHERE tag_text LIKE ? || '%'"
sqlInsertNewTag = "INSERT INTO doc_tags (tag_text, create_date) VALUES (?, date('now'))"
sqlInsertTagLink = "INSERT INTO n_docs_tags (doc_id, tag_id, date('now'))"

sqlLookupAttribs = "SELECT attrib_name FROM doc_attributes WHERE attrib_name LIKE ? || '%'"
sqlInsertNewAttrib = "INSERT INTO doc_attributes (attrib_name, attrib_value, create_date) VALUES (?, ?, date('now'))"
sqlInsertNewAttribLink = "INSERT INTO n_docs_attribs (doc_id, attrib_id, create_date) VALUES (?, ?, date('now'))"

# Code:

class TagSelector(npyscreen.wgautocomplete.Autocomplete):

    valueList = []
    currValOffset = 0
    displayString = ''

    def clear_values(self):
        self.valueList = []
        pass

    def get_values(self):
        return self.valueList
    
    def auto_complete(self, input):

        global dbCur, dbConn, sqlLookupTags, sqlInsertNewTag
        locTxtResList = []

        currValue = self.value[self.currValOffset:]
        
        # Is this tag in the database?

        locFldSrchVal = currValue
        logging.debug("Searching for the token " + locFldSrchVal)
        locResult = dbCur.execute(sqlLookupTags, [locFldSrchVal, ])
        locFldResList = locResult.fetchall()

        for txtVal in locFldResList:
            locTxtResList.append(txtVal[0])

        # If there are no results, add this to the database

        if len(locTxtResList) == 0:
            logging.debug("Did not find " + currValue + ", adding it to the database")
            dbCur.execute(sqlInsertNewTag, [locFldSrchVal, ])
            dbConn.commit()
        else:
            # If there ARE results, present a chooser
            currValue = str(locTxtResList[self.get_choice(locTxtResList)])

        # Append this value to the list:
        self.valueList.append(currValue)

        self.currValOffset = self.currValOffset + len (currValue) + 2
        self.displayString = self.displayString + currValue + '; '
        self.value = self.displayString
        self.cursor_position=len(self.value)

        pass

class TitleTagSelector(npyscreen.wgtitlefield.TitleText):
    _entry_type = TagSelector


class AttributeSelector(npyscreen.wgautocomplete.Autocomplete):

    valueList = []
    currValOffset = 0
    displayString = ''

    def clear_values(self):
        self.valueList = []
        pass

    def get_values(self):
        return self.valueList
    
    def auto_complete(self, input):

        global dbCur, dbConn, sqlLookupAttribs
        locTxtResList = []

        currValue = self.value[self.currValOffset:]
        
        # Is this attribute in the database?

        locFldSrchVal = currValue
        logging.debug("Searching for the attribute token " + locFldSrchVal)
        locResult = dbCur.execute(sqlLookupTags, [locFldSrchVal, ])
        locFldResList = locResult.fetchall()

        for txtVal in locFldResList:
            locTxtResList.append(txtVal[0])

        currValue = str(locTxtResList[self.get_choice(locTxtResList)])

        # currValue is the attribute name



        # Append this value to the list:
        self.valueList.append(currValue)

        self.currValOffset = self.currValOffset + len (currValue) + 2
        self.displayString = self.displayString + currValue + '; '
        self.value = self.displayString
        self.cursor_position=len(self.value)

        pass

class TitleAttributeSelector(npyscreen.wgtitlefield.TitleText):
    __entry_type = AttributeSelector


class ScannerSessionForm(npyscreen.FormBaseNew):

    def create(self):

        self.sessFld = self.add(npyscreen.TitleFixedText, name = "Current Session:", )
        self.docNbr = self.add(npyscreen.TitleFixedText, name = "Document Number:", )
        self.fldTags = self.add(TitleTagSelector, name = "Tags:", )
        self.fldAttribs = self.add(TitleAttributeSelector, name = "Attributes:", )
        self.fldEffDt = self.add(npyscreen.TitleDateCombo, name = "Effective Date:", )
        self.fldNumPgs = self.add(npyscreen.TitleSlider, name = "Number of Pages:", out_of = 16)
        self.tagList = self.add(npyscreen.TitlePager, name= "Current Tags:", )

    def while_editing(self, arg):

        # If the tag does not exist in the database, add it.  Then update the tagList.
                
        if (arg is self.fldAttribs or arg is self.docNbr) and (len(self.fldTags.entry_widget.get_values()) > 0):
            self.tagList.values.append(self.fldTags.entry_widget.get_values())
            for itm in self.fldTags.entry_widget.get_values():
                logging.debug("Appending item: " + itm)
            self.tagList.display()
            self.fldTags.entry_widget.clear_values()

        pass

class SimDocApp(npyscreen.NPSApp):

    def main(self):

        MF = ScannerSessionForm(name = "SIMple DOCument ManaGeR")

        MF.edit()

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
