### Sync.py

The script synchronizes two directories - the source and the replica. Synchronization is one-way, the contents of the replica directory are converted to the contents of the source.
Copy and delete operations are logged to a file and output to the console.
Only standard Python libraries are used.
The paths to directories, the synchronization interval and the path to the log file are set by command line parameters when starting the program.
Usage:
To run the program in the console, enter:

For Windows users - enter paths to directories and the path to the log file must be specified in quotation marks.
