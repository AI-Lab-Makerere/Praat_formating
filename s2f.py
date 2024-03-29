import argparse
import csv
import os
from pydub import AudioSegment
from parse_textgrid import remove_empty_lines, TextGrid
from pydub.utils import which

AudioSegment.converter = which("ffmpeg")

# FIXME the segments overwrite each other - add a file specific prefix
# FIXME create a new csv file then append all segments to it..

parser = argparse.ArgumentParser(
    description='Convert segments to common voice format files')
parser.add_argument('--input-dir')
# parser.add_argument('input_annotation')
#parser.add_argument('--output-audio-path', default='/home/sha3bola/repos/rcrops/segment_to_file_util/')
#parser.add_argument('--output-csv-path', default='/home/sha3bola/repos/rcrops/segment_to_file_util/')
parser.add_argument('--output-prefix', default='seg')

from utils import ensure_files_and_folders_exist

args = parser.parse_args()

ensure_files_and_folders_exist(args.input_dir)

files_in_dir = os.listdir(args.input_dir)
for file_in_dir in files_in_dir:

    if file_in_dir in ["clips", "JUNK_clips", "MUSIC_clips", "PHONE_clips", "INCOMPLETE_clips", "OVERLAPPING_clips"]:
        continue

    if os.path.splitext(file_in_dir)[1] not in [".ogg", ".mp3", ".wav"]:
        # print(file_in_dir)
        continue

    audio_file_path = os.path.join(args.input_dir, file_in_dir)
    annotation_file_path = os.path.join(args.input_dir, "{}.TextGrid".format(os.path.splitext(file_in_dir)[0]))

    
    assert os.path.splitext(audio_file_path)[0] == os.path.splitext(annotation_file_path)[0]
    assert os.path.exists(audio_file_path)
    

    try:
        assert os.path.exists(annotation_file_path)
    except:
       
        timestamp = os.path.splitext(file_in_dir.split('_T')[1])[0]
        annotation_file_name = "{}_T{}.TextGrid".format(file_in_dir.split('_T')[0], timestamp.replace('.','_'))
        annotation_file_path = os.path.join(args.input_dir, annotation_file_name)

        assert os.path.exists(annotation_file_path)


    try:
        if audio_file_path.split(".")[-1] == "mp3":
            main_audio_file = AudioSegment.from_mp3(audio_file_path)
        elif audio_file_path.split(".")[-1] == "wav":
            main_audio_file = AudioSegment.from_wav(audio_file_path)
        elif audio_file_path.split(".")[-1] == "ogg":
            main_audio_file = AudioSegment.from_ogg(audio_file_path)
        
    except:
        err_fd = open("errors.txt", "a+")
        err_fd.write(annotation_file_path)
        err_fd.close()
        continue

    try:
        f = open(annotation_file_path, "rb")
        text = f.readlines()
        text = remove_empty_lines(text)
        main_annotation_file = TextGrid(text)
        f.close()

    except Exception as e:
        print("ERR: {}".format(str(e)))
        err_fd = open("errors.txt", "a+")
        err_fd.write(annotation_file_path)
        err_fd.close()
        continue

    number_of_items = len(main_annotation_file.tier_list[0]['items'])
    segment_files_list = []  # (file_path, text)
    file_prefix = os.path.splitext(audio_file_path)[0].split("/")[-1]
    for i in range(number_of_items):

        segment_to_seperate = main_annotation_file.tier_list[0]['items'][i]
        segment_xmin = float(segment_to_seperate["xmin"]) * 1000
        segment_xmax = float(segment_to_seperate["xmax"]) * 1000
        total_segment_duration = segment_xmax - segment_xmin
        # print(type(segment_xmin))
        # print(segment_xmin)
        # print(type(segment_xmax))
        # print(segment_xmax)
        segment_audio = main_audio_file[segment_xmin:segment_xmax]
        segment_text = segment_to_seperate["text"]
        segment_audio_path = file_prefix + "_" + args.output_prefix + str(i) + ".mp3"

        if segment_text.lower() in ["junk.", "junk"]:

            segment_audio = segment_audio.set_channels(1)
            segment_audio.export(
                args.input_dir + "/" + "JUNK_clips" + "/" +  segment_audio_path, format="wav")

        elif segment_text.lower() in ["music.", "music"]:
            segment_audio = segment_audio.set_channels(1)
            segment_audio.export(
                args.input_dir + "/" + "MUSIC_clips" + "/" + segment_audio_path, format="mp3")

        elif segment_text.lower() in ["phone call.", "phone call", "phone speech.", "phone speech"]:
            segment_audio = segment_audio.set_channels(1)
            segment_audio.export(
                args.input_dir + "/" + "PHONE_clips" + "/" + segment_audio_path, format="mp3")

        elif total_segment_duration >= 30000 or segment_text.lower().rstrip().lstrip() == "":
            segment_audio = segment_audio.set_channels(1)
            segment_audio.export(
                args.input_dir + "/" + "INCOMPLETE_clips" + "/" + segment_audio_path, format="mp3")

        elif segment_text.lower() in ["overlap.", "overlapping.", "overlap", "overlapping"]:
            segment_audio = segment_audio.set_channels(1)
            segment_audio.export(
                args.input_dir + "/" + "OVERLAPPING_clips" + "/" + segment_audio_path, format="mp3")

        else:
            segment_audio = segment_audio.set_channels(1)
            segment_audio.export(
                args.input_dir + "/" + "clips" + "/" + segment_audio_path, format="wav")

        segment_files_list.append(
            (segment_audio_path, segment_text, total_segment_duration))

    csv_file_path = args.input_dir + "/" + "index" + ".csv"
    # with open(csv_file_path, "a") as csv_fd:
    csv_fd = open(csv_file_path, "a+")
    jk_csv_file_path = args.input_dir + "/" + "junk" + ".csv"
    jk_fd = open(jk_csv_file_path, "a+")
    music_csv_file_path = args.input_dir + "/" + "music" + ".csv"
    music_fd = open(music_csv_file_path, "a+")
    phone_csv_file_path = args.input_dir + "/" + "phone" + ".csv"
    phone_fd = open(phone_csv_file_path, "a+")
    incomplete_csv_file_path = args.input_dir + "/" + "incomplete" + ".csv"
    incomplete_fd = open(incomplete_csv_file_path, "a+")
    overlapping_csv_file_path = args.input_dir + "/" + "overlapping" + ".csv"
    overlapping_fd = open(overlapping_csv_file_path, "a+")

    csvwriter = csv.writer(csv_fd,
                           quotechar='|', quoting=csv.QUOTE_MINIMAL)
    jk_csvwriter = csv.writer(jk_fd,
                              quotechar='|', quoting=csv.QUOTE_MINIMAL)
    music_csvwriter = csv.writer(music_fd,
                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
    phone_csvwriter = csv.writer(phone_fd,
                                 quotechar='|', quoting=csv.QUOTE_MINIMAL)
    incomplete_csvwriter = csv.writer(incomplete_fd,
                                      quotechar='|', quoting=csv.QUOTE_MINIMAL)
    overlapping_csvwriter = csv.writer(overlapping_fd,
                                       quotechar='|', quoting=csv.QUOTE_MINIMAL)

    for path, text, duration in segment_files_list:
        if text.lower().strip(" .!") in ["junk"]:
            jk_csvwriter.writerow([str(path), str(text),  str(duration)])
        elif text.lower().strip(" .!") in ["music"]:
            music_csvwriter.writerow([str(path), str(text),  str(duration)])
        elif text.lower().strip(" .!") in ["phone call", "phone speech"]:
            phone_csvwriter.writerow([str(path), str(text),  str(duration)])
        elif total_segment_duration >= 30000 or text.lower().rstrip().lstrip() == "":
            incomplete_csvwriter.writerow(
                [str(path), str(text),  str(duration)])
        elif segment_text.lower().strip(" .!") in ["overlap", "overlapping"]:
            overlapping_csvwriter.writerow(
                [str(path), str(text),  str(duration)])
        elif segment_text.lower().strip(" .!") in ["advert", "radio jingle", "phone contact"]:
            pass
        else:
            csvwriter.writerow([str(path), str(text),  str(duration)])
