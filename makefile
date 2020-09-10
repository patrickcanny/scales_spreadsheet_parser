install:
	pip3 install -r requirements.txt

setup:
	mkdir Scales_Intl
	mkdir Scales_Intl/Pro_Prelims
	touch Scales_Intl/Pro_Prelims/thumbs.csv
	mkdir Scales_Intl/Pro_Finals
	touch Scales_Intl/Pro_Finals/thumbs.csv
	mkdir Scales_Intl/Amateur
	touch Scales_Intl/Amateur/thumbs.csv
	mkdir Scales_Intl/Over_30
	touch Scales_Intl/Over_30/thumbs.csv

run:
	make setup
	python3 spreadsheet_parser.py

clean:
	rm -rf Scales_Intl
	rm *Titles.txt
