#!/usr/bin/python
import sys, subprocess, json, os
import argparse

def cutter(item_c):
    while item_c.find('[') != -1:
        start = item_c.find('[')
        end = item_c.find(']')
        number = ''
        if end-start <= 3:
            number = item_c[start+1:end]
        item_c = item_c[0:start]+item_c[end+1:len(item_c)]
        if item_c.find('[') == -1:
            while item_c.find('(') != -1:
                start = item_c.find('(')
                end = item_c.find(')')
                item_c = item_c[0:start]+item_c[end+1:len(item_c)]
        if number != '':
            item_c = item_c[0:-4]+' '+number+item_c[-4:len(item_c)]
        while item_c.find('_') != -1:
            _num = item_c.find('_')
            item_c = item_c[0:_num]+item_c[_num+1:len(item_c)]
        while item_c.find(' .') != -1:
            item_c = item_c[0:item_c.find(' .')]+item_c[item_c.find('_')-3:len(item_c)]
        l_fix.append(item_c)
        print item_c
        number = ''

parser = argparse.ArgumentParser(description='--dir')
parser.add_argument("--dir", help="Use --dir <dir_after_DIR>for find change and conver in include dir")
args = parser.parse_args()
f_dir = args.dir
print(f_dir)

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = dir_path[:dir_path.find('/to_aru_anime_converter')]
dir_path += '/Download_mount/' + f_dir

#Psycho-Pass Sinners of the System Case.1

l_root = []
l_fix = []
full_root = []

count = 0

print "Move find dir:"+dir_path
for root, dirs, files in os.walk(dir_path): 
    for file in files:   
        if file.endswith('.mkv') | file.endswith('.mp4') | file.endswith('.avi'): 
            full_root.append(str(root+'/'+str(file))) 
            l_root.append(str(root))
            check = (str(root+'/'+str(file)))
#           print check
            output = subprocess.check_output([
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=codec_name", 
                "-of", "default=noprint_wrappers=1:nokey=1",
                check
            ])[:-1]
            if  output == 'h264':
#               print output
#               print (str(file))
                cutter(str(file))
                output = subprocess.check_output([
                    "ffprobe",
                    "-v", "error",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    check
                ])
            data = json.loads(output)
            format, streams = [data[k] for k in ('format','streams')]

            for s in streams:
                if s['codec_type'] == 'video':
                    print 'Stream #{} {}'.format(s['index'], s['codec_type'])
                    print 'Codec: {}'.format(s['codec_name'])
                    print 'Resolution: {}x{}'.format(
                        s.get('width', '?'), s.get('height', '?'))
                elif s['codec_type'] == 'audio':
                    print 'Stream #{} {}'.format(s['index'], s['codec_type'])
                    print 'Codec: {}'.format(s['codec_name'])
                    print 'Sample Rate: {}'.format(s.get('sample_rate', '?'))
count=0
for i in l_fix:
    print full_root[count]
    print i
    print full_root[count][0:-4] + '.ass'
    if os.path.exists(full_root[count][0:-4] + '.ass'): 
        output = subprocess.check_output([
            "cp",
            full_root[count][0:-4]+'.ass',
            str(l_root[count]+'/'+i[0:-4]+'.ass')
        ])

    output = subprocess.check_output([
        "ffmpeg",
        "-i", full_root[count],
        "-c:v", "libx265",
        "-x265-params", "crf=25",
        "-c:a", "copy", 
        str(l_root[count]+'/'+i)  
    ])
#    output = subprocess.check_output([
#        "cp",
#        full_root[count][0:-3]
#
#        ])
    count +=1

