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
    successful_download_names = []
    thumbnail_path = '/Users/colinbeckford/Desktop/Scales/Thumbnail Pictures/'
    ending = ""
    if division_name == 'Amateur':
        ending = '_A'
    elif division_name == 'Pro Finals':
        ending = '_F'
    elif division_name == 'Pro Prelims':
        ending = '_P'
    # download to a folder that will be zipped later
    download_folder = './Open/' + '_'.join(division_name.split(' '))
    try:
        os.mkdir(download_folder)
    except Exception:
        pass
    for freestyle in freestyles:
        url = freestyle['Freestyle Link']
        player_name = freestyle['Name']
        if freestyle['Order']:
            order = freestyle['Order']
            order = str(order).zfill(3)
        else:
            print('There is no order value for ' + player_name + '\'s freestyle.')
            order = 999

        # prepend order to be able to sort the videos 
        new_video_name = str(order) +  ' Scales Open V4 ' + division_name + ' - ' + player_name

        try:
            # setup youtube object
            video = pt.YouTube(url).streams.first()
            video.download(output_path=download_folder, filename=new_video_name)
            print('Downloaded ' + player_name + '\'s ' + division_name)
            first_name = player_name.split(' ')[0]
            last_initial = player_name.split(' ')[1][0]
            upper_name = player_name.upper()
            thumb = thumbnail_path + first_name + last_initial + ending + '.jpg'
            csv_vals = list(upper_name.split(' '))
            csv_vals.append(thumb)
            csv_string = ",".join(csv_vals)
            successful_download_names.append(csv_string)
        except pt.exceptions.VideoUnavailable as e:
            print('-- Video Unavailable -------------------------')
            print (e)
            print(player_name + '\'s ' + division_name + ' video is unavailable. Please contact them and have them re-upload.')
            unavailable_freestyles.append(str(player_name + ' ' + division_name))
            print('-- Video Unavailable -------------------------')
        except Exception as e:
            print('--EXCEPTION -------------------------')
            print(e)
            print('This is an issue with ' + player_name + '\'s ' + division_name + ', try downloading this video manually.')
            failed_downloads.append(player_name + '-' + str(url))
            print('--EXCEPTION -------------------------')
        
        print()

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

    if len(successful_download_names) > 0:
        successes = sorted(list(set(successful_download_names)))
        successes.insert(0, 'FirstName,LastName')
        successful_dl_names = open(download_folder + '/' + division_name + '_Downloaded_Players.csv', 'w+')
        successful_dl_names.writelines(map(lambda x: x+'\n', successes))
        successful_dl_names.close()

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
            video_title = f'Scales Open Vol. 4 - {division_name} - {place} - {name}'
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
try:
    os.mkdir('Open')
except Exception:
    pass
option = ''
print('1. download all freestyles')
print('2. download pro prelims')
print('3. download pro finalists')
print('4. download amateur')
print('5. download non-finaist pro freestyles')
print('6. Generate All Video Titles')
print('7. exit')
print()
print('Select an option (1-6):')
for line in fileinput.input():
    option = line.rstrip()
    if option == '1':
        download_by_division('Pro Prelims', pro_prelims)
        download_by_division('Amateur', amateurs)
        download_by_division('Pro Finals', pro_finalists)
        download_by_division('Non Finalists', pro_finals_did_not_final)
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
        download_by_division('Non Finalists', pro_finals_did_not_final)
        break
    elif option == '6':
        generate_titles('Pro Prelims',pro_prelims)
        generate_titles('Pro Finals',pro_finalists)
        generate_titles('Amateur',amateurs)
        break
    elif option == '7':
        print('bye (-:')
        break
