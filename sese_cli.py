from core.transcribe import SeseTranscribe
from core.translate import SeseTranslate
from core.splitwma import SeseSplitWma
import os
class SeseCli:
    def __init__(self,config) -> None:
        self.funcMode = config["functionMode"]
        self.whip_model=SeseTranscribe(config)
        self.input_path=config["inputpath"]
        self.translate_module=SeseTranslate(config)
        self.translate_save_path=config["translate"]["save_path"] 
        self.splitwma=SeseSplitWma(config)
        
        
        
    def run(self):
        
        if(self.funcMode == "transcribe"):
            self.only_trancribe_process()
        elif(self.funcMode == "asmr"):
            self.asmr_process()
        elif(self.funcMode == "avi"):
            self.avi_process()
            
        else:
            raise Exception("invalid funcMode")
        
    def only_trancribe_process(self,):
        if(os.path.isfile(self.input_path)):
                self.whip_model.run(self.input_path)
        elif(os.path.isdir(self.input_path)):
            for item in os.listdir(self.input_path):
                self.whip_model.run(os.path.join(self.input_path,item))
        else:
            raise Exception("invalid file path")
    
    def asmr_process(self):
        if(os.path.isfile(self.input_path)):
            lrc_reu=self.whip_model.run(self.input_path)
            trans_save_path=os.path.join(os.path.dirname(self.input_path), os.path.splitext(os.path.basename(self.input_path))[0]+"_transed.lrc")
            self.translate_module.run(lrc_reu,trans_save_path)
        elif(os.path.isdir(self.input_path)):
            lrc_reu=[]
            for item in os.listdir(self.input_path):
                single_lrc_resu=self.whip_model.run(os.path.join(self.input_path,item))
                trans_save_path=os.path.join(self.translate_save_path, os.path.splitext(item)[0]+"_transed.lrc")
                self.translate_module.run(single_lrc_resu,trans_save_path)
        else:
                raise Exception("invalid file path")
        print("[***]  all task complete. ")
    
    def avi_process(self):
        if(os.path.isfile(self.input_path)):
            audio_path=self.splitwma.run(self.input_path)
            print("[***] audio file save in %s"%audio_path)
            #检查是否已经转录
            srt_path=os.path.join(os.path.dirname(audio_path),"%s.srt"%(os.path.splitext(os.path.basename(audio_path))[0]))
            if(not os.path.exists(srt_path)):
                srt_resu=self.whip_model.run(audio_path,process_video=True)
            else:
                srt_resu=self.translate_module.srt_reverse(srt_path)
            trans_save_path=os.path.join(os.path.dirname(self.input_path), os.path.splitext(os.path.basename(self.input_path))[0]+"_transed.srt")
            self.translate_module.run(srt_resu,trans_save_path,process_video=True)
            
    
    def filetype_check(self,filename):
        if(filename[-3:].lower() in ["mp4","avi"]):
            return 0
        elif(filename[-3:].lower() in ["mp3","wma","wav"]):
            return 1
        else:
            return 2 #invalid filetype