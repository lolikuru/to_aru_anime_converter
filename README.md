# to_aru_anime_converter

need be installed:
- ffmpeg
- python 2.7
- mediainfo(for frame counter)

Python script for 
- converting h264 to h265 with ffmpeg
- cut any [] and () 
- convert directory
- copy ass files
- rename ass files
- change output for using in jenkins
- find files in path '/Download_mount/' for default

import sys, subprocess, json, os, argparse

example: 
jenkins@ubuntuworkstation:~/workspace/Convert_to_h265/to_aru_anime_converter$ python find_h264.py --dir 'Psycho-Pass Sinners of the System Case.1'

output dir:~/workspace/Convert_to_h265/Download_mount/<dirVideofound>/

output file:
- 'Psycho-Pass Sinners of the System - 01.mp4'
- 'Psycho-Pass Sinners of the System - 01.ass'
