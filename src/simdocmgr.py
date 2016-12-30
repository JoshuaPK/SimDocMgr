#!/usr/bin/python

# Simple DOCument ManaGeR
# Copyright 2016 Joshua Kramer

# Process Flow:
# (As of 31-DEC-2016 command line not supported)

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
import getpass
from datetime import datetime

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
dbConn.isolation_level = None
dbCur = dbConn.cursor()

# SQL Queries:

sqlLookupTags = "SELECT tag_text FROM doc_tags WHERE tag_text LIKE ? || '%'"
sqlInsertNewTag = "INSERT INTO doc_tags (tag_text, create_date) VALUES (?, date('now'))"
sqlInsertTagLink = "INSERT INTO n_docs_tags (doc_id, tag_id, date('now'))"
sqlInsertNewDoc = "INSERT INTO documents (doc_path, doc_filename, create_date, eff_date, create_user, doc_name) VALUES (?, ?, 'now', ?, ?, ?)"

sqlLookupAttribs = "SELECT attrib_name FROM doc_attributes WHERE attrib_name LIKE ? || '%'"
sqlInsertNewAttrib = "INSERT INTO doc_attributes (attrib_name, attrib_value, create_date) VALUES (?, ?, date('now'))"
sqlInsertNewAttribLink = "INSERT INTO n_docs_attribs (doc_id, attrib_id, create_date) VALUES (?, ?, date('now'))"

# Load Debugger:

# from pudb.remote import set_trace
# set_trace(term_size=(80,24))

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


class ScannerSessionForm(npyscreen.FormBaseNew):


    def create(self):

        locHlpTxt = '^S: Scan; ^D: New Document; ^R: Import PDF; ^X: Exit'
        self.hlpText = self.add(npyscreen.TitleFixedText, value=locHlpTxt, name = 'Shortcuts: ', editable=False, use_two_lines = False, )
        self.fldSess = self.add(npyscreen.TitleFixedText, editable=False, name = 'Current Session: ', value = '0', use_two_lines = False, )
        self.docNbr = self.add(npyscreen.TitleFixedText, editable=False, name = 'Document Number: ', value = '1', use_two_lines = False, )
        self.fldTags = self.add(TitleTagSelector, name = 'Tags:', )
        self.fldEffDt = self.add(npyscreen.TitleDateCombo, name = 'Effective Date:', use_two_lines = False)
        self.fldNumPgs = self.add(npyscreen.TitleSlider, name = 'Number of Pages:', lowest = 1, out_of = 16, use_two_lines = False)
        self.tagList = self.add(npyscreen.TitlePager, name= 'Current Tags:', scroll_exit = True,   )

        self.fldNumPgs.value = 1

        self.add_handlers({"^S": self.do_scan})
        self.add_handlers({"^D": self.new_document})
        self.add_handlers({"^R": self.import_pdf})
        self.add_handlers({"^X": self.exit_app})

    def while_editing(self, arg):

        # If the tag does not exist in the database, add it.  Then update the tagList.

        if (arg is self.fldEffDt) and (len(self.fldTags.entry_widget.get_values()) > 0):
            for locVal in self.fldTags.entry_widget.get_values():
                self.tagList.values.append(locVal)
            for itm in self.fldTags.entry_widget.get_values():
                logging.debug("Appending item: " + itm)
            self.tagList.display()
            self.fldTags.entry_widget.clear_values()

        pass

    def make_out_dir(self):
        """Based on the current session ID, make the correct output directory.
            Returns the full file path."""

        global dataDir

        locFullDir = os.path.abspath(dataDir)
        locDocDir = locFullDir + '/Documents/' + self.fldSess.value
        os.mkdir(locDocDir)

        return locDocDir

        pass

    def save_doc_info(self):
        """Save the tags and effective date, if any, in the database"""



        pass



    def do_scan(self, other_arg):

        global dbCur, dbConn, sqlInsertTagLink, sqlInsertNewDoc, sqlInsertNewTag


        locProceed = npyscreen.notify_ok_cancel('Scanning Now!', 'Scan Dialog')
        logging.debug("Control+S pressed, do_scan running")

        scanEngine = ScannerEngine()
        locSession = self.fldSess.value
        locDocNbr = self.docNbr.value

        locNumPgs = int(self.fldNumPgs.value)
        locOutDir = self.make_out_dir()

        if locProceed:
            locDocFn = scanEngine.scanPages(locNumPgs, locOutDir)

        # Put stuff in the database.

        dbCur.execute('begin')

        # Prepare document variables and insert document information

        locDocPath = '../Documents/' + self.fldSess.value + '/'
        locEffDate = self.fldEffDt.value

        locDateObj = datetime.strptime(locEffDate, '%d %B, %Y').date()
        locEffDate = locDateObj.strftime('%Y-%m-%d')
        locDocName = locDocFn
        locUser = getpass.getuser()

        logging.debug('Inserting document record into database for ' + locDocName)

        dbCur.execute(sqlInsertNewDoc, [locDocPath, locDocFn, locUser, locEffDate, locDocName,])
        locDocId = dbCur.lastrowid

        logging.debug('Document ID is ' + str(locDocId))

        # Prepare tag variables

        locTagList = self.tagList.values

        for locTagVal in locTagList:

            logging.debug('Inserting new Tag ' + locTagVal + ' for document id ' + str(locDocId))

            dbCur.execute(sqlInsertNewTag, [locTagVal,])
            locTagId = dbCur.lastrowid

            logging.debug('Tag ID is ' + str(locTagId))
            logging.debug('Inserting tag link for tag id ' + str(locTagId) + ' to document ID ' + str(locDocId))

            dbCur.execute(sqlInsertTagLink, [locDocId, locTagId,])

        logging.debug('Committing to database')
        dbCur.execute('commit')

        pass

    def new_document(self, other_arg):

        locProceed = npyscreen.notify_ok_cancel('Create New Document?', 'Command Dialog', editw = 2)

        if locProceed is False:
            return

        locDocNbr = int(self.docNbr.value)
        locDocNbr = locDocNbr + 1
        self.docNbr.value = str(locDocNbr)

        # Do other stuff

        self.DISPLAY()

        pass

    def import_pdf(self, other_arg):

        # Do Stuff

        pass

    def exit_app(self, other_arg):


        pass


class SimDocApp(npyscreen.NPSApp):

    def __init__(self, options_dict = None):
        self.current_session = ''
        self.current_document_number = 1

        if options_dict is not None:
            # Must have been run from command line
            logging.debug("In SimDocApp class __init__, there are options")

        else:
            logging.debug("In SimDocApp class __init__, no options")

            pass

        # Generate the session ID
        sess_dt_part = datetime.now().strftime('%Y%m%d%H%M')
        self.current_session = sess_dt_part

    def main(self):

        MF = ScannerSessionForm(name = "SIMple DOCument ManaGeR")
        MF.fldSess.value = self.current_session
        MF.docNbr.value = str(self.current_document_number)

        MF.edit()

        pass

    def show_error(errText):


        pass

class ScannerEngine:

    def import_pdf(inPath, outPath):
        """Copies a PDF file to the data directory"""

        cpString = inPath + ' ../' + outPath
        logging.info("Copying file using args: " + cpString)

        p = subprocess.Popen(['/usr/bin/cp', cpString], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cpOut, cpErr = p.communicate()
        p = None

        logging.info(cpOut)
        logging.warning(cpErr)


        pass


    def scan_pages(sessId, docNbr, nbrPages, outPath):
        """ Scans nbrPages pages and combines them into a PDF with a temporary file name,
            then renames the pdf to session_id+docNbr and puts it in in outPath """

        global scanpagePrg, scanpageOpts, convertPrg, convertOps, dataDir
        global dbCur, dbConn, sqlLookupTags, sqlInsertNewTag


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

            if i < nbrPages:
                per_page_pause(i, nbrPages )

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
        # Rename it appropriately.

        newFn = sessID + '-d' + docNbr + '.pdf'
        mvString = tmpFn + ' ' + newFn
        p = subprocess.Popen(['/usr/bin/mv', mvString], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mvOut, mvErr = p.communicate()
        p = None

        logging.info(mvOut)
        logging.warning(mvErr)


        # Build the cpString- the command to copy the file to its final location.

        cpString = newFN + ' ../' + outPath
        logging.info("Copying file using args: " + cpString)

        p = subprocess.Popen(['/usr/bin/cp', cpString], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cpOut, cpErr = p.communicate()
        p = None

        logging.info(cpOut)
        logging.warning(cpErr)

        # Now, remove the temp directory.
        os.chdir('..')
        shutil.rmtree(tmpLoc)

        return newFn

    # All done!

    pass


def per_page_pause(locCurPg, locTotPgs):
    """Displays a 'Press Key to Scan Next Page' box after each page scan is complete."""

    locMsg = 'Press OK to scan page ' + str(locCurPg) + ' of ' + str(locTotPgs)
    npyscreen.notify_confirm(locMsg, title='Message', editw=1)


    pass


def do Stuff():

    #scanPages(2, 'test_loc')
    sdApp = SimDocApp()
    sdApp.run()

    pass

if __name__ == '__main__':


    doStuff()

    pass
