# SimDocMgr: SIMple DOCument ManaGeR

The goal of SimDocMgr is simple: provide an interface for you to scan paper documents into PDF files, then attach tags and effective dates to those documents.

## Concept

As of 08-JAN-2017, SimDocMgr consists of a simple console interface based on npyscreen (which uses ncurses).

### First Run

1. Create a virtualenv and put the src, log, and data directories under it.
2. Activate the virtualenv and pip install npyscreen.
3. Make sure you have the command line tools for ImageMagick and sane-backends.
4. Create the sqlite3 database.
5. Go into src and run python ./simdocmgr.py

### Data Structure

Logs are put in the 'log' directory; data resides under 'data'.  The SQLite3 schema is located under data.  At this point it is a simple list of documents, tags, and links between the two.

Under 'data', there is a 'Documents' directory.  Each time you start the program, it generates a session ID which consists of a timestamp: YYYYMMDDHHMM.  A directory is created under that Documents directory with the session ID as the name.  Documents that are scanned during that session are scanned into individual PDF files with the session name and a numerical suffix as the filename.  You can add new documents from the UI.

### Entering Tags

For each tag you enter, you need to press Tab.  This will look in the tag table in the database.  If there are no tags, or if there are no tags that start with the tag you just entered, then the tag will be added in the database.  If there are tags that start with the tag you just entered, you will be presented with a list to choose the tags.  For example, you enter 'New' and press tab.  It isn't in the database, so it adds the tag.  You enter 'New York' and press tab again, and it does the same.  You go on and scan the document.  Several documents later, you have a document related to New York.  So you type 'New' and press tab.  You are presented with a list where you can select 'New' or 'New York'.

If you want to enter a tag that consists of the first letters of some other tag- for example, you want to enter 'Dog' when the only thing in the database is 'Dog Food'- then you can scroll down to the bottom of the list and select the entry for 'Tag Not In List'.

### Other Settings

When you first start the program, you are prompted to choose the scanner that you want to use.

You can also choose the Effective Date of the document, as well as the number of pages, using the controls on the add document form.

## Roadmap

1. Write a GUI program to retrieve the documents.  (This is planned to be written using pyQt.)
2. Add the 'Import PDF' functionality so that we can import documents that are already PDFs.
3. Properly handle multipage/document fed scanners.
4. Integrate pyOCR so that you can scan all your documents to one PDF, and SimDocMgr will go into the PDF, splitting and tagging documents as required.
5. Provide scanner controls.  Some scanners have more capabilities than others, and it would be nice to control those settings within the UI.
6. Make the scanning application into a GUI instead of npyscreen.

## License

GNU GPL v2.0

