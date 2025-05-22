#!/usr/bin/python
import subprocess, os
import argparse, time


extra_symbol_list = ["`"]
format_list = ['3GP' , 'avi' ,'mkv', 'mp4', 'avi', 'MOV', 'mov', 'MPG', 'wmv', 'flv', 'MP4']

print('Formats for converting: ')
print(' '.join(format_list))

sub_postfix = ['.ass', '.srt']
sub_langs = [ 'rus', 'eng']
include_sub_dir = [ '', 'subtitles', 'Subtitles' ]

def du(path):
    """disk usage in human readable format (e.g. '2,1GB')"""
    return subprocess.check_output(['du','-sh', path]).split()[0].decode('utf-8')

def original_delete(delete_root):
    print('DANGER, ORIGINALS DELETING')
    output = subprocess.check_output([
        "rm",
        delete_root
        ])

def frame_count(input_root):
#    print(input_root)
    for s in extra_symbol_list:
        input_root = input_root.replace( s, "\\" + s)
    cmd ="ffmpeg -i \"" + input_root + "\" -vcodec copy -acodec copy -f null /dev/null 2>&1 | grep -Eo 'frame= *[0-9]+ * | tail -1'"
    frame_count = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=None, shell=True)
    out = frame_count.communicate()
#    print(out)
    if (out[-1] is None):
        out = out[-2]
    else: 
        out = out[-1]
#    print(out)
    out = out.split('\n')[-2]
    out = out.replace(' ', '')
    out = out[6:]
    time.sleep(2)
#    print("\'"+out+"\'")
#    frame_count = frame_count[frame_count.find('Frame count'):frame_count.find('\n', frame_count.find('Frame count'))]
#    frame_count = frame_count[frame_count.find(':')+2:] 
    return out

def check_included_subs(full_path):
    output = subprocess.check_output([
        "ffprobe",
        "-v", "error",
        "-select_streams", "s:0",
        "-show_entries", "stream=codec_name",
        "-of", "default=noprint_wrappers=1:nokey=1",
        full_path
        ])[:-1]
    if output in ['ass', 'srt']:
        print("Subs found in file " + full_path)
        return True
    else: 
        return False

def cutter(item_c):
    item_verified = item_c
    print(item_c)
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
        item_c = item_c[0:item_c.rfind('.')] + " HEVC" + item_c[-4:len(item_c)]
    if item_c[-4:len(item_c)] != '.mkv':
        item_c = item_c[0:item_c.rfind('.')] + '.mkv'
    print(item_c)
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
    print('Original files will be deleted after converting')
else: 
    print('Converting w/o origins deleting')

if args.only_check:
    print('Only check')

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = dir_path[:dir_path.find('/to_aru_anime_converter')]
dir_path += '/Download_mount' + f_dir


l_root = []
l_fix = []
full_root = []

count = 0

print("Move find dir:"+dir_path)
print(du(dir_path))
for root, dirs, files in os.walk(dir_path): 
    for f_file in files:
        if f_file[f_file.rfind('.'):] in sub_postfix:
            if f_file[0:f_file.find('.')] != f_file.split('.')[-2]:
                if f_file.split('.')[-2] not in sub_langs:
                   sub_langs.append(f_file.split('.')[-2])
        #print(f_file.split('.')[-1])
        if f_file.split('.')[-1] in format_list:
            if str(f_file).find('HEVC') == -1:
                check = (str(root +'/' + str(f_file)))
                output = subprocess.check_output([
                    "ffprobe",
                    "-v", "error",
                    "-select_streams", "v:0",
                    "-show_entries", "stream=codec_name", 
                    "-of", "default=noprint_wrappers=1:nokey=1",
                    check
                ])[:-1]
                if  output in ['h264', 'mpeg4']:
                    full_root.append(str(root +'/' + str(f_file)))
                    l_root.append(str(root))
                    cutter(str(f_file))
count = 0

for index,prop_sub_dir in enumerate(include_sub_dir):
    if prop_sub_dir != '':
        include_sub_dir[index] = include_sub_dir[index] + '/'
        print(include_sub_dir[index])

for i in l_fix:
    print("New name is " + i)
    for prop_sub_dir in include_sub_dir: 
        for name in sub_postfix:
#        print(full_root[count][0:-4] + '.ass ' + str(os.path.exists(full_root[count][0:-4] + '.ass')))
#        print(l_root[count]+'/'+i[0:-4]+'.ass ' + str(os.path.exists(l_root[count]+'/'+i[0:-4]+'.ass')))
            if os.path.exists(full_root[count][0:-4] + name):
                if not os.path.exists(l_root[count]+'/'+i[0:-4] + name): 
                    print('cp ' + full_root[count][0:-4] + name + ' ' + l_root[count]+'/'+i[0:-4] + name)
                    if not args.only_check:
                        output = subprocess.check_output([
                            "cp",
                            full_root[count][0:-4] + name,
                            l_root[count]+'/'+i[0:-4] + name
                        ])

                if args.delete_origin:
                    output = subprocess.check_output([
                        "rm",
                        full_root[count][0:-4] + name
                    ])
            
            for lang in sub_langs:
                proposed_sub_path = l_root[count] + '/' + prop_sub_dir + full_root[count][full_root[count].rfind('/')+1:-4] + "." + lang + name
                new_sub_path = l_root[count]+'/'+ prop_sub_dir + i[0:-4] + '.' + lang + name

               # print('Old sub path ' + proposed_sub_path)
               # print('New sub path ' + new_sub_path)

                if os.path.exists(proposed_sub_path):
                    if not os.path.exists(l_root[count]+'/'+ prop_sub_dir + i[0:-4] + '.' + lang + name):
                        print('cp ' + proposed_sub_path + ' ' + new_sub_path)
                        if not args.only_check:
                            output = subprocess.check_output([
                                "cp",
                                proposed_sub_path,
                                new_sub_path
                            ])

                    if args.delete_origin:
                        output = subprocess.check_output([
                            "rm",
                            proposed_sub_path
                        ])


    if os.path.exists(str(l_root[count]+'/'+i)):
        output_file_frames = frame_count(l_root[count]+'/'+i)
        input_file_frames = frame_count(full_root[count])
        if input_file_frames != output_file_frames:
            print ((float(input_file_frames) - int(output_file_frames))/int(input_file_frames)*100)
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
        #process = "ffmpeg -i '" + full_root[count] + "' -c:v libx265 -x265-params crf=25 -c:a copy '" + str(l_root[count]+'/'+i) + " -y'"
        f_count = frame_count(full_root[count])
        if not args.only_check:
            copy_sub = []
            if check_included_subs(full_root[count]):
                copy_sub = ["-map", "0:s"]
                print(copy_sub)
            #print("ffmpeg -loglevel warning -hide_banner -stats -i '\"+ full_root[count] + "\' -c:v libx265 -x265-params crf=26 -codec:a aac -map 0 \'" + str(l_root[count]+'/'+i+"\'"))
            p = subprocess.Popen([
                "ffmpeg",
                "-loglevel", "warning",
                "-hide_banner", "-stats",
                "-i", full_root[count],
                "-c:v", "libx265",
                "-x265-params", "crf=26",
                "-codec:a", "copy",
                "-codec:s", "copy",
                "-map", "0:v",
                "-map", "0:a?" ]
                + copy_sub + 
                [ "-y", str(l_root[count]+'/'+i) ],
                stderr=subprocess.PIPE)
            drop = ''
            conv = ''
            full_frame = 0
            if args.verbose:
                chatter = p.stderr.read(1024)
                while chatter.rstrip() != '':
                    out = chatter.rstrip()
                    chatter = p.stderr.read(1024)
                    out = out.split('\n')
                    for x in out:
                        print (x)
                        if chatter.find('frame='):
                            if chatter.find('drop=')!=-1 & chatter.find('speed=')!=-1:
                                drop = chatter[chatter.find('drop=')+5:chatter.find('speed=')]
                                drop = drop.replace(' ', '')
                            if chatter.find('frame=')!=-1 & chatter.find('fps=')!=-1:
                                conv = chatter[chatter.find('frame=')+6:chatter.find('fps=')]
                                conv = conv.replace(' ', '') 
#                           if drop.isdigit() and conv.isdigit():
#                               full_frame = int(drop)+int(conv)
#                               print(f_count + " =?< " + str(full_frame))
#                   if args.delete_origin and full_frame >= f_count:
#                       original_delete(full_root[count])
            else:
                out_r = 0
                chatter = p.stderr.read(64)
                while chatter.rstrip() != '':
                    chatter = p.stderr.read(64)
                    if chatter.find('frame=')!=-1 & chatter.find('fps=')!=-1:
                        out = chatter[chatter.find('frame=')+6:chatter.find('fps=')]
                        out = out.replace(' ', '')
                        if chatter.find('drop=')!=-1 & chatter.find('speed=')!=-1:
                            drop = chatter[chatter.find('drop=')+5:chatter.find('speed=')]
                            drop = drop.replace(' ', '')
                        if drop.isdigit() and conv.isdigit():
                            full_frame = int(drop)+int(conv)
                            if int(out_r) <= full_frame:
                                out_r = full_frame
                                n = float(out_r)/int(f_count)
                                print("Output Name:" + i + " {:.2%}".format(n) + " Frames compiled:" + str(out_r))
#                if args.delete_origin:
#                    original_delete(full_root[count])

    if os.path.exists(str(l_root[count]+'/'+i)) and os.path.exists(str(full_root[count])):
        input_final_count = int(frame_count(full_root[count]))
        output_final_count = int(frame_count(l_root[count]+'/'+i))
        print("Frame count original:" + str(input_final_count))
        print("Frame count HEVC:" + str(output_final_count))
        percentage = (float(input_final_count) - output_final_count)/input_final_count*100
        print(str(percentage) + "% not identity")
        if percentage < 2:
            if args.delete_origin:
                print("< 2%, it's correct")
                original_delete(full_root[count])
    count +=1

print(du(dir_path))



