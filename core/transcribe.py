from faster_whisper import WhisperModel
import re
import os

class SeseTranscribe():
    def __init__(self, config) -> None:
        self.model_type=config["transcribe"]["model_type"]
        os.environ["CUDA_VISIBLE_DEVICES"] = '0'
        self.model = WhisperModel(self.model_type, device="cuda", compute_type="int8_float16")

        # if(os.path.isdir(config["inputpath"])):
        #     out_dir=os.path.join(config["inputpath"],"output") 
        # elif(os.path.isfile(config["inputpath"])):
        #     out_dir =os.path.join(os.path.dirname(config["inputpath"]),"output") 
            
        # #创建输出文件夹
        # if not os.path.exists(out_dir):
        #     os.makedirs(out_dir)
        
    def run(self, audio_file):
        out_filename=os.path.splitext(os.path.basename(audio_file))[0]
        out_path=os.path.join(os.path.dirname(audio_file),f"{out_filename}.lrc" )
        #判断输出文件是否存在且不为空
        if(os.path.exists(out_path) and os.path.getsize(out_path) > 0):
            print("jp lrc file exist, restore file %s"%(out_filename))
            return self.RestoreLrcFile(out_path)
        print("[***] start transcribe file: %s"%(os.path.basename(audio_file)))
        # segments, info = model.transcribe("audio.mp3", beam_size=5)
        segments, info = self.model.transcribe(audio_file, beam_size=5)
        
        print(f"saving in {out_path}....")
        lrc_resu=self.save_to_lrc(segments, out_path)
        return lrc_resu
    
    def format_time(self, seconds):
        # 将秒转换为 LRC 文件中使用的时间格式 [mm:ss.xx]
        m, s = divmod(seconds, 60)
        ms = int((s - int(s)) * 100)
        return '[{:02}:{:02}.{:02}]'.format(int(m), int(s), ms)

    '''
    input:
        transcription: the transcription result after model
        lrc_path: lrc save path
    output:
        list->[(time_tick, content),...] pair result
    '''
    def save_to_lrc(self, transcription, lrc_path):
        lrc_list=[]
        # print("[***] the line number of transcribe is %d"%len(list(transcription)))
        # import pdb;pdb.set_trace()
        with open(lrc_path, "w", encoding="utf-8") as lrc_file:
            lrc_file.write("[AI translate]\n")
            for segment in transcription:
                timetick=self.format_time(segment.start)
                lrc_file.write(f"%s %s\n" % (timetick,  segment.text))
                lrc_list.append((segment.start,segment.text))
        print("[***] origin lrc file comlete.")
        return lrc_list

    def RestoreLrcFile(self,outpath):
        pattern = r"\[([^\]]+)\] (.*)"
        lrc_list=[]
        with open(outpath,encoding="utf-8") as fp:
            lines=fp.readlines()
        for line in lines[1:]:
            match = re.match(pattern, line)
            if match:
                time_text = match.group(1)
                lyric_text = match.group(2)
                # import pdb;pdb.set_trace()
                time_sec=self.reverse_format_time(time_text)
                lrc_list.append((time_sec,lyric_text))
        return lrc_list
                
    
    def reverse_format_time(self,time_text):
        """将[分:秒.毫秒]格式转换回秒"""  
        pattern = r"(\d+):(\d+).(\d+)"
        match = re.match(pattern, time_text)
        if match:
            m, s, ms = match.groups()
            m, s, ms = int(m), int(s), int(ms)
            seconds = m * 60 + s + ms / 100.0
            return seconds
        else:
            return 0
    
    def merge_redundant_senten(self,lrc_list):
        after_merge=[]
        candidate=lrc_list[0]
        cand_time=lrc_list[0][0]
        for item in lrc_list[1:]:
            if(len(item[1])>len(candidate[1])):
                if(candidate[1] in item[1]):
                    candidate=item
                else:
                    after_merge.append((cand_time, candidate[1]))
                    cand_time=item[0]
                    candidate=item
            else:
                if(item[1] not in candidate[1]):
                    after_merge.append((cand_time, candidate[1]))
                    cand_time=item[0]
                    candidate=item
        after_merge.append((cand_time, candidate[1]))

        return after_merge
    
    def merge_timegap(self,lrc_list):
        base_time=lrc_list[0][0]
        after_time_align=[]
        after_time_align.append(lrc_list[0])
        for item in lrc_list[1:]:
            if(item[0]-base_time<1): #间隔小于1s的pass
                pass
            else:
                base_time=item[0]
                after_time_align.append(item)
        return after_time_align