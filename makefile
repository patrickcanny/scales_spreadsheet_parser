install:
	pip3 install -r requirements.txt

setup:
	mkdir Scales_VI
	mkdir Scales_VI/Pro_Prelim
	touch Scales_VI/Pro_Prelim/thumbs.csv
	mkdir Scales_VI/Pro_Final
	touch Scales_VI/Pro_Final/thumbs.csv
	mkdir Scales_VI/Amateur
	touch Scales_VI/Amateur/thumbs.csv
	mkdir Scales_VI/Over_30
	touch Scales_VI/Over_30/thumbs.csv

run:
	python3 spreadsheet_parser.py

clean:
	rm -rf Scales_VI
	rm *Titles.txt
