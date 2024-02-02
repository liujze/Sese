#encoding:utf-8
'''
从视频中分离wma,保存到临时文件夹
'''

import os
import ffmpeg

class SeseSplitWma():
    def __init__(self, filename) -> None:
        '''
        filetype: 0视频/1音频/2非法值
        '''
        assert(len(filename)>=3)
        self.filename=filename
        self.audio_file=None
        
        if(filename[-3:].lower() in ["mp4","avi"]):
            self.filetype = 0
        elif(filename[-3:].lower() in ["mp3","wma","wav"]):
            self.filetype = 1
        else:
            raise Exception("invalid filename")
        
        self.name = os.path.splitext(os.path.basename(filename))[0]
        
        #创建临时文件夹
        curdir = os.getcwd()
        tmp_dir = os.path.join(curdir, 'tmp')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
    
    def run(self):
        if(self.filetype==0):
            self.split_wma()
        
            
    def split_wma(self):
        self.audio_file = f'{self.name}.mp3' 
        in_file =ffmpeg.input(self.filename)
        audio_stream = in_file.audio
        out_file = ffmpeg.output(audio_stream, os.path.join('tmp',self.audio_file))
        out_file.run()
        
        
        