install:
	pip3 install -r requirements.txt

run:
	python3 spreadsheet_parser.py

clean:
	rm -rf Scales_Intl
	rm *Titles.txt
