for file in ../../Open/Amateur/*.mp4; do
    if [ -f "$file" ]; then
        echo "$file"
        echo "python2 ../upload.py --file='$file' --title='$file' --description='Scales Open V4 is Brought to You by the Scales Collective' --keywords='yoyo, scales' --category='22' --privacyStatus='unlisted'"
        python2 ../upload.py --file="$file" --title="$file" --description="Scales Open V4 is Brought to You by the Scales Collective" --keywords="yoyo, scales" --category="22" --privacyStatus="unlisted"
    fi
done
