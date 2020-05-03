# Scales Spreadsheet Parser
Download all freestyles from a spreadsheet, renaming them and saving them to a good folder structure

## Installation
Prerequisites: 
- GNU make (if you want to use the makefile commands, you can also run the makefile commands without make)
- Python 3
- An active credentials JSON (you'll need to get this from patrick or create it yourself)

1. Clone this
2. Use command `make install` to download the requirements
3. Use command `make run` to execute the program
4. Use command `make clean` to remove the 'Open' folder if you do not need the files anymore (perhaps after you zip the folder)

## Setup 
When you get the credentials file from Patrick, you may want to add a new spreadhseet to be parsed. The steps for doing this are pretty straightforward

1. Go to the spreadsheet you want to add in Google Drive
2. Find the 'client_email' key in the credentials JSON and copy that email.
3. Share the Google Drive Spreadsheet with this email.
4. Update Line 75 in the `spreadsheet_parser.py` program with the name of the sheet you are wanting to download
5. `make run`

## Troubleshooting
The parser has several features that aid in troubleshooting when not all videos can be downloaded.

1. There is useful debug output as the script downloads videos.
2. You have the option to view statistics regarding the number of freestyles of each type. To view this, make sure that the variable `DEBUG` is set to `True` on line 17.
3. You can also view the JSON structure of freestyles. You will need to make the `SHOW_FREESTYLES` variable `True` to see these.
4. There are log files included in the folders with the downloaded videos. These files allow you to quickly see the videos with download issues. Refer to these files to see the issues. 
