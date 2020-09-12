install:
	pip3 install -r requirements.txt

setup:
	mkdir Scales_Intl
	mkdir Scales_Intl/Pro_Prelim
	touch Scales_Intl/Pro_Prelim/thumbs.csv
	mkdir Scales_Intl/Pro_Final
	touch Scales_Intl/Pro_Final/thumbs.csv
	mkdir Scales_Intl/Amateur
	touch Scales_Intl/Amateur/thumbs.csv
	mkdir Scales_Intl/Over_30
	touch Scales_Intl/Over_30/thumbs.csv

run:
	python3 spreadsheet_parser.py

clean:
	rm -rf Scales_Intl
	rm *Titles.txt
