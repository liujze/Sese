#encoding:utf-8
'''
从视频中分离wma,保存到临时文件夹
'''

import os
import ffmpeg
# import moviepy.editor as mp

class SeseSplitWma():
    def __init__(self, config) -> None:
        '''
        filetype: 0视频/1音频/2非法值
        '''
        pass
    
    def run(self, filename):
        assert(len(filename)>=3)
        out_path=self.split_wma(filename)
        return out_path
        
            
    def split_wma(self,filename):
        name = os.path.splitext(os.path.basename(filename))[0]
        audio_file = f'{name}.mp3' 
        out_path=os.path.join(os.path.dirname(filename),audio_file)
        if(os.path.exists(out_path)):
            print("[***] audio file is exist")
            return out_path
        
        # out_path=os.path.join(os.path.dirname(filename),audio_file)
        # video_fp = mp.VideoFileClip(filename)
        # video_fp.audio.write_audiofile(out_path)
        in_file =ffmpeg.input(filename)
        audio_stream = in_file.audio
        
        out_file = ffmpeg.output(audio_stream, out_path,f='mp3')
        out_file.run()
        return out_path
        
        
        