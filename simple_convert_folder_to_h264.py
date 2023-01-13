#!/usr/bin/python
import subprocess, os
import argparse, time
import ffmpeg

extra_symbol_list = ["`"]
format_list = ['mkv', 'mp4', 'avi', 'MOV', 'mov']


def du(path):
    """disk usage in human readable format (e.g. '2,1GB')"""
    return subprocess.check_output(['du', '-sh', path]).split()[0].decode('utf-8')


def original_delete(delete_root):
    print('DANGER, ORIGINALS DELETING')
    output = subprocess.check_output([
        "rm",
        delete_root
    ])


dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = dir_path[:dir_path.find('/to_aru_anime_converter')]
dir_path += '/Download_mount'

print(du(dir_path))

for root, dirs, files in os.walk(dir_path):
    for f_file in files:
        print f_file
        (
            ffmpeg
            .input(root + '/' + f_file)
            .filter('fps', fps=30, round='up')
            .output(root + '/' + f_file[:f_file.find('.')] + '_h264.mp4', format='h264')
            .run()
        )

# (
#    ffmpeg
#        .input('input.mp4')
#        .hflip()
#        .output('output.mp4')
#        .run()
# )
