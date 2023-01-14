#!/usr/bin/python
import subprocess, os
import argparse, time
import ffmpeg

extra_symbol_list = ["`"]
format_list = ['mkv', 'mp4', 'avi', 'MOV', 'mov', "MP4"]


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
        print(f_file.split('.')[-1])
        if f_file.find('_h264') == -1:
            if f_file.split('.')[-1] in format_list:
                print f_file
                in1 = ffmpeg.input(root + '/' + f_file)
                a1 = in1.audio

                (
                    ffmpeg
                    .input(root + '/' + f_file)
                    # .filter('fps', fps=30, round='up')
                    .filter('vidstabdetect', shakiness=3, accuracy=15)
                    .output('-', format='null')
                    .run()
                )
                (
                    ffmpeg
                    .input(root + '/' + f_file)
                    .filter('vidstabtransform', smoothing=3, zoom=-3)
                    .filter('fps', fps=30, round='up')
                    .output(a1, 'step1.mp4')
                    .overwrite_output()
                    .run()
                )
                (
                    ffmpeg
                    .input('step1.mp4')
                    .filter('vidstabdetect', shakiness=4, accuracy=15)
                    .filter('fps', fps=30, round='up')
                    .output('-', format='null')
                    .overwrite_output()
                    .run()
                )
                (
                    ffmpeg
                    .input('step1.mp4')
                    .filter('vidstabtransform', smoothing=12, zoom=0)
                    .filter('fps', fps=30, round='up')
                    .output(a1, root + '/' + f_file[:f_file.find('.')] + '_h264.mp4')
                    .overwrite_output()
                    .run()
                )

# (
#    ffmpeg
#        .input('input.mp4')
#        .hflip()
#        .output('output.mp4')
#        .run()
# )
