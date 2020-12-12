#!/usr/bin/python
import sys, subprocess, json, os
import argparse, time

def frame_count(input_root):
    cmd ="ffmpeg -i \'" + input_root + "\' -vcodec copy -acodec copy -f null /dev/null 2>&1 | grep -Eo 'frame= *[0-9]+ * | tail -1'"
    frame_count = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=None, shell=True)
    
#    print fframe_count.communicate()[0]
    out = frame_count.communicate()[0]
    out = out.split('\n')[-2]
    out = out.replace(' ', '')
    out = out[6:]
    time.sleep(2)
    #print("\'"+out+"\'")
#    frame_count = frame_count[frame_count.find('Frame count'):frame_count.find('\n', frame_count.find('Frame count'))]
#    frame_count = frame_count[frame_count.find(':')+2:]  
    return out

def cutter(item_c):
    item_verified = item_c
    print item_c
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
        if item_c[0] == ' ':
            item_c = item_c[1:len(item_c)]
#        print item_c
        number = ''
    if item_c == item_verified:
        item_c = item_c[0:item_c.find('.')] + " HEVC" + item_c[-4:len(item_c)]
    print item_c
    l_fix.append(item_c)


parser = argparse.ArgumentParser(description='--dir')
parser.add_argument("--dir", action="store", dest="dir", 
        help="Use --dir <dir_after_DIR>for find change and conver in include dir")
parser.add_argument("--delete_origin", action="store_true", dest="delete_origin",
        help="Delete origin file after converting and rename")
parser.add_argument("--only_check", action="store_true", dest="only_check",
        help="Check files only w/o deletion and convertaion")
parser.add_argument("--v", action="store_true", dest="verbose",
        help="Verbose convertation")
args = parser.parse_args()
if args.dir:
    f_dir = "/" + args.dir
else: f_dir = '' 

#print(f_dir)
if args.delete_origin:
    print 'Original files will be deleted after converting'
else: 
    print 'Converting w/o origins deleting'

if args.only_check:
    print 'Only check'

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = dir_path[:dir_path.find('/to_aru_anime_converter')]
dir_path += '/Download_mount' + f_dir


l_root = []
l_fix = []
full_root = []

count = 0

print "Move find dir:"+dir_path
for root, dirs, files in os.walk(dir_path): 
    for file in files:   
        if file.endswith('.mkv') | file.endswith('.mp4') | file.endswith('.avi'): 
            if str(file).find('HEVC') == -1:
                check = (str(root+'/'+str(file)))
                output = subprocess.check_output([
                    "ffprobe",
                    "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=codec_name", 
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    check
                ])[:-1]
                if  output in ['h264', 'mpeg4']:
                    full_root.append(str(root+'/'+str(file)))
                    l_root.append(str(root))
                    cutter(str(file))
count = 0
for i in l_fix:
    print i
    print(full_root[count][0:-4] + '.ass ' + str(os.path.exists(full_root[count][0:-4] + '.ass')))
    print(l_root[count]+'/'+i[0:-4]+'.ass ' + str(os.path.exists(l_root[count]+'/'+i[0:-4]+'.ass')))
    if os.path.exists(full_root[count][0:-4] + '.ass'):
        if not os.path.exists(l_root[count]+'/'+i[0:-4]+'.ass'): 
            print 'cp ' + full_root[count][0:-4] + '.ass ' + l_root[count]+'/'+i[0:-4]+'.ass'
            if not args.only_check:
                output = subprocess.check_output([
                    "cp",
                    full_root[count][0:-4]+'.ass',
                    l_root[count]+'/'+i[0:-4]+'.ass'
                ])
        if args.delete_origin:
            output = subprocess.check_output([
                "rm",
                full_root[count][0:-4]+'.ass'
            ])

    if os.path.exists(str(l_root[count]+'/'+i)):
        output_file_frames = frame_count(l_root[count]+'/'+i)
        input_file_frames = frame_count(full_root[count])
        if input_file_frames != output_file_frames:
            print ("Frames is not correct for "+i)
            print ("Input file frames:" + input_file_frames)
            print ("Output file frames:"+ output_file_frames)
            output = subprocess.check_output([
                "rm",
                "-v",
                str(l_root[count]+'/'+i)
            ])
            time.sleep(2)
            print ("Unconverted file deleted " + i)
        else: 
            print ("Video already converted " + i)
            print ("Input file frames:" + input_file_frames)
            print ("Output file frames:"+ output_file_frames)

    if not (os.path.exists(str(l_root[count]+'/'+i))):
        process = "ffmpeg -i '" + full_root[count] + "' -c:v libx265 -x265-params crf=25 -c:a copy '" + str(l_root[count]+'/'+i) + "'"
        f_count = frame_count(full_root[count])
        if not args.only_check:
            p = subprocess.Popen([
                "ffmpeg",
                "-i", full_root[count],
                "-c:v", "libx265",
                "-x265-params", "crf=25",
                "-codec:a", "aac", 
                str(l_root[count]+'/'+i)],
                stderr=subprocess.PIPE)
            if args.verbose:
                chatter = p.stderr.read(1024)
                while chatter.rstrip() != '':
                    out = chatter.rstrip()
                    chatter = p.stderr.read(1024)
                    print(out)
            else:
                out_r = 0
                chatter = p.stderr.read(64)
                while chatter.rstrip() != '':
                    chatter = p.stderr.read(64)
#                    print(chatter)
                    if chatter.find('frame=')!=-1 & chatter.find('fps=')!=-1:
                        out = chatter[chatter.find('frame=')+6:chatter.find('fps=')]
#                       print ('\'' + out + '\'')
                        out = out.replace(' ', '')
                        if out != '':
                            if int(out_r) <= int(out):
                                out_r = out
                                n = float(out_r)/int(f_count)
                                print("Output Name:" + i + " {:.2%}".format(n) + " Frames compiled:" + out)
    if (os.path.exists(str(l_root[count]+'/'+i))):
        if frame_count(full_root[count]) == frame_count(l_root[count]+'/'+i):
            if args.delete_origin:
                print 'DANGER, ORIGINALS DELETING'
                output = subprocess.check_output([
                   "rm",
                    full_root[count]
                ])
    count +=1


