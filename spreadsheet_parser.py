# Scales Spreadsheet Parser
# @author Patrick Canny 04/01/2020
# @description Read freestyle data from a google spreadsheet, download and sort
# the submitted videos into folders, renaming the videos along the way

# ------------------------------------Third Party Packages
import gspread
import pprint
import pytube as pt
from oauth2client.service_account import ServiceAccountCredentials

# ------------------------------------Python Packages
import os
import fileinput

# Debugging variables, ideally we can set these in the script at runtime
DEBUG = False
SHOW_FREESTYLES = False

# @function download_by_division given a division name and a list of freestyles
# for that division, download them into an appropriate folder
# @param division_name a string that represents the divison name
# @param freestyles a list of freestyles
def download_by_division(division_name, freestyles):
    failed_downloads = []
    unavailable_freestyles = []
    for freestyle in freestyles:
        url = freestyle['Freestyle Link']
        player_name = freestyle['Name']
        if freestyle['Order']:
            order = freestyle['Order']
        else:
            print('There is no order value for ' + player_name + '\'s freestyle.')
            order = 999

        # prepend order to be able to sort the videos 
        new_video_name = str(order) +  ' Scales Open V4 ' + division_name + ' - ' + player_name

        try:
            # setup youtube object
            video = pt.YouTube(url).streams.first()

            # download to a folder that will be zipped later
            download_folder = './Open/' + '_'.join(division_name.split(' '))
            video.download(output_path=download_folder, filename=new_video_name)
            print('Downloaded ' + player_name + '\'s ' + division_name)
        except pt.exceptions.VideoUnavailable:
            print(player_name + '\'s ' + division_name + ' video is unavailable. Please contact them and have them re-upload.')
            unavailable_freestyles.append(str(player_name + ' ' + division_name))
        except:
            print('There was an unknown issue with ' + player_name + '\'s ' + division_name + ', try downloading this video manually.')
            failed_downloads.append(str(url))

    # After everything is done, write the failed downloads and unavilable
    # videos to a file in the appropriate folder
    if len(failed_downloads) > 0:
        failed_dl_file = open(download_folder + '/_failed_downloads.txt', 'w+')
        failed_dl_file.writelines(map(lambda x: x+'\n', failed_downloads))
        failed_dl_file.close()

    if len(unavailable_freestyles) > 0:
        unavailable_videos_file = open(download_folder + '/_unavailable_videos.txt', 'w+')
        unavailable_videos_file.writelines(map(lambda x: x+'\n', unavailable_freestyles))
        unavailable_videos_file.close()

    # wrap up
    print('Done with ' + division_name)


# Setup Service account
scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
        ]
credentials = ServiceAccountCredentials.from_json_keyfile_name('Scales-79fd55601efd.json', scope)
client = gspread.authorize(credentials)

# Open the spreadsheet we want to look at
sheet = client.open('Vol. 4 Freestyles').sheet1

# Grab all the submitted freestyles from the sheet
freestyles = sheet.get_all_records()
pp = pprint.PrettyPrinter()

# filter the freestyles by round
amateurs = list( filter(lambda x: x['Round of Video'] == 'Amateur', freestyles) )
pro_prelims = list( filter(lambda x: x['Round of Video'] == 'Pro Prelim', freestyles) )
pro_finals = list( filter(lambda x: x['Round of Video'] == 'Pro Final', freestyles) )

# filter the submitted pro finals by who made finals
pro_finals_did_not_final = list(
        filter(lambda x: x['Made Finals'] == 0, pro_finals))
pro_finalists = list(
        filter(lambda x: x['Made Finals'] == 1, pro_finals))

# Print the freestyle lists
if SHOW_FREESTYLES:
    pp.pprint(amateurs)
    pp.pprint(pro_prelims)
    pp.pprint(pro_finals_did_not_final)
    pp.pprint(pro_finalists)

# Print the number of total freestyles (sanity check)
if DEBUG:
    print('number of total freestyles: ' + str(len(freestyles)))
    print('number of amateur freestyles: ' + str(len(amateurs)))
    print('number of pro prelim freestyles: ' + str(len(pro_prelims)))
    print('number of pro final freestyles: ' + str(len(pro_finals)))
    print('number of pro final freestyles that did not final: ' +
            str(len(pro_finals_did_not_final)))
    print('number of pro finalists ' +
            str(len(pro_finalists)))
# I/O
option = ''
print('1. download all freestyles')
print('2. download pro prelims')
print('3. download pro finalists')
print('4. download amateur')
print('5. download non-finaist pro freestyles')
print('6. exit')
print()
print('Select an option (1-6):')
for line in fileinput.input():
    option = line.rstrip()
    if option == '1':
        download_by_division('Pro Prelims', pro_prelims)
        download_by_division('Amateur', amateurs)
        download_by_division('Pro Finals', pro_finalists)
        download_by_division('Non Finalists', pro_finalists_did_not_final)
        break
    elif option == '2':
        download_by_division('Pro Prelims', pro_prelims)
        break
    elif option == '3':
        download_by_division('Pro Finals', pro_finalists)
        break
    elif option == '4':
        download_by_division('Amateur', amateurs)
        break
    elif option == '5':
        download_by_division('Non Finalists', pro_finalists_did_not_final)
        break
    elif option == '6':
        print('bye (-:')
        break
