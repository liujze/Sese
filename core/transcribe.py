from faster_whisper import WhisperModel
import time
import os

class SeseTranscribe():
    def __init__(self, config) -> None:
        self.model_type=config["transcribe"]["model_type"]
        self.model = WhisperModel(self.model_type, device="cuda", compute_type="int8_float16")

        # if(os.path.isdir(config["inputpath"])):
        #     out_dir=os.path.join(config["inputpath"],"output") 
        # elif(os.path.isfile(config["inputpath"])):
        #     out_dir =os.path.join(os.path.dirname(config["inputpath"]),"output") 
            
        # #创建输出文件夹
        # if not os.path.exists(out_dir):
        #     os.makedirs(out_dir)
        
    def run(self, audio_file):
        print("[***] start transcribe file: %s"%(os.path.basename(audio_file)))
        # segments, info = model.transcribe("audio.mp3", beam_size=5)
        segments, info = self.model.transcribe(audio_file, beam_size=5)
        out_filename=os.path.splitext(os.path.basename(audio_file))[0]
        out_path=os.path.join(os.path.dirname(audio_file),f"{out_filename}.lrc" )
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
            for segment in transcription:
                timetick=self.format_time(segment.start)
                lrc_file.write(f"%s %s\n" % (timetick,  segment.text))
                lrc_list.append((segment.start,segment.text))
        print("[***] origin lrc file comlete.")
        return lrc_list


        
    