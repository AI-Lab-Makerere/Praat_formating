import argparse
import csv
import os
from pydub import AudioSegment
from parse_textgrid import remove_empty_lines, TextGrid
from pydub.utils import which

def ensure_files_and_folders_exist(input_dir):

    for folder_name in ["clips", "JUNK_clips", "MUSIC_clips", 
                    "PHONE_clips", "INCOMPLETE_clips", "OVERLAPPING_clips"]:

        
        if not os.path.exists(input_dir + "/{}/".format(folder_name)):
            os.mkdir(input_dir + "/{}".format(folder_name))

    
    for file_name in ["index",  "junk", "music", "phone", "incomplete", "overlapping"]:

        if os.path.exists(input_dir + "/" + file_name + ".csv"):
            os.remove(input_dir + "/" + file_name + ".csv")



