# Scales Spreadsheet Parser
# @author Patrick Canny 04/01/2020
# @description Read freestyle data from a google spreadsheet, download and sort
# the submitted videos into folders, renaming the videos along the way

# ------------------------------------Third Party Packages
import gspread
import pprint
import pytube as pt
from pytube import YouTube
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------------------Python Packages
import os
import fileinput
import subprocess
import re
import traceback
import time
from multiprocessing import Pool
import string

# Debugging variables, ideally we can set these in the script at runtime
DEBUG = False
SHOW_FREESTYLES = False
NUM_THREADS = 1

# constants used for changing values for specific contests
SHEET_NAME = 'Scales Open V6 Freestyle Submission (Responses)'
ROOT_FORM_NAME = 'Form Responses 1'
CONTEST_NAME = 'Scales_Open_VI'
CONTEST_FOLDER_NAME = 'Scales_VI'
VIDEO_LINK_COL = 'Video File Upload'
VIDEO_NAME_COL = 'Generated Video Name'
PLAYER_NAME_COL = 'Competitor Name'

# TODO change this, probably
THUMBNAIL_FOLDER = './Thumbnails/'

successful_dl_names = []

def dl_pro_pre(row):
    return yt_dl(row, 'Pro_Prelim', '_P')

def dl_pro_final(row):
    return yt_dl(row, 'Pro_Final', '_F')

def dl_x_pre(row):
    return yt_dl(row, 'X_Prelim', '_XP')

def dl_x_final(row):
    return yt_dl(row, 'X_Final', '_XF')

def dl_am(row):
    return yt_dl(row, 'Amateur', '_A')

def dl_int(row):
    return yt_dl(row, 'Intermediate', '_INT')

def dl_int(row):
    return yt_dl(row, 'Intermediate', '_INT')

def dl_creative(row):
    return yt_dl(row, 'Creative', '_CREATIVE')

def dl_over_30(row):
    return yt_dl(row, 'Over_30', '_30')

def yt_dl(row, division_name='NO_DIV', ending=''):
    url = row[VIDEO_LINK_COL]
    player_name = row[PLAYER_NAME_COL]
    new_video_name = row[VIDEO_NAME_COL]
    should_dl = row['Uploaded?'] != 'y'

    if not should_dl:
        return

    try:
        order = row['Order']
        order = str(order).zfill(3)
    except KeyError:
        print('There is no order value for ' + player_name + '\'s freestyle.')
        order = 999

    yt_dl_command = ''

    # url setup
    base = 'youtube-dl --no-check-certificate --write-thumbnail'

    # always get best we can
    quality_control = '-f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"'

    # location
    location = f'-o \'./{CONTEST_FOLDER_NAME}/{division_name}/{new_video_name}.mp4\''

    yt_dl_command = ' '.join([base, location, quality_control, url])
    print(yt_dl_command)
    try:
        subprocess.call(yt_dl_command, shell=True)
    except Exception as e:
        print('--EXCEPTION -------------------------')
        print(e)
        traceback.print_exc()
        print('--EXCEPTION -------------------------') 

    thumbnail_path = THUMBNAIL_FOLDER
    first_name = player_name.split(' ')[0].translate(str.maketrans('', '', string.punctuation))
    try:
        last_name = player_name.split(' ')[1].translate(str.maketrans('', '', string.punctuation))
    except IndexError:
        last_name = ''
    upper_name = player_name.translate(str.maketrans('', '', string.punctuation)).upper()
    thumb = thumbnail_path + first_name + '_' + last_name + ending + '.jpg'
    csv_vals = [first_name,last_name,thumb]
    csv_string = ",".join(csv_vals)
    print('---------------------------------------')
    print(csv_string)
    print('---------------------------------------')

    return(csv_string)

# @function download_by_division given a division name and a list of freestyles
# for that division, download them into an appropriate folder
# @param division_name a string that represents the divison name
# @param freestyles a list of freestyles
def download_by_division(division_name, freestyles):
    failed_downloads = []
    unavailable_freestyles = []
    dl_function = None
    # change if needed
    thumbnail_path = THUMBNAIL_FOLDER

    ending = ""
    if division_name == 'Amateur':
        dl_function = dl_am
        ending = '_A'
    if division_name == 'Intermediate':
        dl_function = dl_int
        ending = '_INT'
    elif division_name == 'Pro_Final':
        dl_function = dl_pro_final
        ending = '_F'
    elif division_name == 'Pro_Prelim':
        dl_function = dl_pro_pre
        ending = '_P'
    elif division_name == 'X_Final':
        dl_function = dl_x_final
        ending = '_XF'
    elif division_name == 'X_Prelim':
        dl_function = dl_x_pre
        ending = '_XP'
    elif division_name == 'Over_30':
        dl_function = dl_over_30
        ending = '_o_30'
    elif division_name == 'Creative':
        dl_function = dl_creative
        ending = '_CREA'


    csvs = map(dl_function, freestyles)
    
    # TODO multithread?
    # with Pool(NUM_THREADS) as pool:
    #     csvs = pool.map(dl_function, freestyles)
    #     pool.close()
    #     pool.join()

    # write csv values to a file
    print(csvs)
    if csvs:
        if not os.path.exists(f'./{CONTEST_FOLDER_NAME}/{division_name}'):
            os.makedirs(f'./{CONTEST_FOLDER_NAME}/{division_name}')
        f = open(f'./{CONTEST_FOLDER_NAME}/{division_name}/thumbs.csv', 'w+')
        f.write('Name,ThumnailPath\n')
        for line in csvs:
            if not line:
                line = 'ERROR'
            f.write(line)
            f.write('\n')
        f.close()

    print('just wrote thumnails to file')

    # wrap up
    print('Done with ' + division_name)


# @function generate_titles - write video titles to a text file sorted by placement 
# @param division_name a string that represents the divison name
# @param freestyles a list of freestyles
def generate_titles(division_name, freestyles):
    print('Generating titles for ' + division_name)
    titles = []
    for freestyle in freestyles:
        if freestyle['Placement']:
            place = freestyle['Placement']
            name = freestyle['Name']
            video_title = f'{CONTEST_NAME} - {division_name} - {place} - {name}'
            titles.append(video_title)
    if len(titles) > 0:
        title_file = open(f'./{division_name}_Titles.txt', 'w+')
        title_file.writelines(map(lambda x: x+'\n', titles))
        title_file.close()
    print('Done with ' + division_name)
    return

# Setup Service account
scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
        ]
credentials = ServiceAccountCredentials.from_json_keyfile_name('Scales-79fd55601efd.json', scope)
client = gspread.authorize(credentials)

# Open the spreadsheet we want to look at
# print(client.list_spreadsheet_files())
sheet_all_freestyles = client.open(SHEET_NAME).worksheet(ROOT_FORM_NAME)
sheet_pro_pre = client.open(SHEET_NAME).worksheet('pro_prelim')
sheet_pro_final = client.open(SHEET_NAME).worksheet('pro_final')
sheet_x_pre = client.open(SHEET_NAME).worksheet('x_prelim')
sheet_x_final = client.open(SHEET_NAME).worksheet('x_final')
sheet_amateur = client.open(SHEET_NAME).worksheet('amateur')
sheet_intermediate = client.open(SHEET_NAME).worksheet('intermediate')
sheet_over_30 = client.open(SHEET_NAME).worksheet('over_30')
sheet_creative = client.open(SHEET_NAME).worksheet('creative_video_contest')

# Grab all the submitted freestyles from the sheet
all_freestyles = list(sheet_all_freestyles.get_all_records())
pro_prelims = list(sheet_pro_pre.get_all_records())
x_finals = list(sheet_x_final.get_all_records())
x_prelims = list(sheet_x_pre.get_all_records())
pro_finals = list(sheet_pro_final.get_all_records())
amateurs = list(sheet_amateur.get_all_records())
intermediate = list(sheet_intermediate.get_all_records())
over_30 = list(sheet_over_30.get_all_records())
creative = list(sheet_creative.get_all_records())

# set up pp
pp = pprint.PrettyPrinter()

# filter the freestyles by round
# amateurs = list( filter(lambda x: x['Round of Video'] == 'Amateur', freestyles) )
# pro_prelims = list( filter(lambda x: x['Round of Video'] == 'Pro Prelim', freestyles) )
# pro_finals = list( filter(lambda x: x['Round of Video'] == 'Pro Final', freestyles) )

# filter the submitted pro finals by who made finals
# pro_finals_did_not_final = list(
#         filter(lambda x: x['Made Finals'] == 0, pro_finals))
pro_finalists = list(
        filter(lambda x: x['Finalist'] == 'Y', pro_finals))

# filter by not upladed
all_freestyles = list(
        filter(lambda x: x['Uploaded?'] == 'y', all_freestyles))

# Print the freestyle lists
if SHOW_FREESTYLES:
    pp.pprint(amateurs)
    pp.pprint(pro_prelims)
    pp.pprint(over_30)
    pp.pprint(pro_finalists)

# Print the number of total freestyles (sanity check)
if DEBUG:
    print('number of amateur freestyles: ' + str(len(amateurs)))
    print('number of pro prelim freestyles: ' + str(len(pro_prelims)))
    print('number of pro finalists ' + str(len(pro_finals)))
    print('number of over 30 ' + str(len(over_30)))
# I/O
try:
    os.mkdir(CONTEST_FOLDER_NAME)
except Exception:
    pass
option = ''
print('1. download all freestyles')
print('2. download pro prelims')
print('3. download pro finals')
print('4. download amateur')
print('5. download over 30')
print('6. Generate All Video Titles')
print('7. download x prelims')
print('8. download x finals')
print('9. download intermediate')
print('10. download creative')
print('11. exit')
print()
print('Select an option (1-6):')
for line in fileinput.input():
    option = line.rstrip()
    if option == '1':
        download_by_division('Pro_Prelim', pro_prelims)
        download_by_division('Amateur', amateurs)
        download_by_division('Pro_Final', pro_finalists)
        download_by_division('Over_30', over_30)
        download_by_division('X_Prelim', x_prelims)
        download_by_division('X_Final', x_finals)
        download_by_division('Intermediate', intermediate)
        download_by_division('Creative', creative)
        break
    elif option == '2':
        download_by_division('Pro_Prelim', pro_prelims)
        break
    elif option == '3':
        download_by_division('Pro_Final', pro_finalists)
        break
    elif option == '4':
        download_by_division('Amateur', amateurs)
        break
    elif option == '5':
        download_by_division('Over_30', over_30)
        break
    elif option == '6':
        generate_titles('Pro_Prelim', pro_prelims)
        generate_titles('Pro_Final', pro_finalists)
        generate_titles('Amateur', amateurs)
        generate_titles('Over_30', over_30)
        break
    elif option == '7':
        download_by_division('X_Prelim', x_prelims)
        break
    elif option == '8':
        download_by_division('X_Final', x_finals)
        break
    elif option == '9':
        download_by_division('Intermediate', intermediate)
        break
    elif option == '10':
        download_by_division('Creative', creative)
        break
    elif option == '11':
        print('bye (-:')
        break
