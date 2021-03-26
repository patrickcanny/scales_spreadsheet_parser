install:
	pip3 install -r requirements.txt

setup:
	mkdir Scales_V
	mkdir Scales_V/Pro_Prelim
	touch Scales_V/Pro_Prelim/thumbs.csv
	mkdir Scales_V/Pro_Final
	touch Scales_V/Pro_Final/thumbs.csv
	mkdir Scales_V/Amateur
	touch Scales_V/Amateur/thumbs.csv
	mkdir Scales_V/Over_30
	touch Scales_V/Over_30/thumbs.csv

run:
	python3 spreadsheet_parser.py

clean:
	rm -rf Scales_V
	rm *Titles.txt
