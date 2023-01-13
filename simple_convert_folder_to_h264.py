import ffmpeg
(
    ffmpeg
    .input('input.mp4')
    .hflip()
    .output('output.mp4')
    .run()
)