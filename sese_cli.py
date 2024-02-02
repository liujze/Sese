from core.transcribe import SeseTranscribe
from core.translate import SeseTranslate
import os
class SeseCli:
    def __init__(self,config) -> None:
        self.funcMode = config["functionMode"]
        self.whip_model=SeseTranscribe(config)
        self.input_path=config["inputpath"]
        self.translate_module=SeseTranslate(config)
        self.translate_save_path=config["translate"]["save_path"] #TODO 处理文件夹时的翻译保存有问题
        
        
        
    def run(self):
        if(self.funcMode == "transcribe"):
            if(os.path.isfile(self.input_path)):
                self.whip_model.run(self.input_path)
            elif(os.path.isdir(self.input_path)):
                for item in os.listdir(self.input_path):
                    self.whip_model.run(os.path.join(self.input_path,item))
            else:
                raise Exception("invalid file path")
        elif(self.funcMode == "asmr"):
            #transcribe
            if(os.path.isfile(self.input_path)):
                lrc_reu=self.whip_model.run(self.input_path)
                # out_path=os.path.join(self.translate_save_path,os.path.splitext(os.path.basename(self.input_path))[0]+"_transed.lrc")
                self.translate_module.run(lrc_reu)
                
                # with open(out_path,"w",encoding="utf-8") as fp:
                #     for time_tick, orig_text in lrc_reu:
                #         trans_text=self.translate_module.run(orig_text)
                #         print(trans_text)
                #         fp.write(f"[%s] %s\n" % (time_tick,  trans_text))
                print("[***]  all task complete. ")
                
                
            elif(os.path.isdir(self.input_path)):
                lrc_reu=[]
                for item in os.listdir(self.input_path):
                    single_lrc_resu=self.whip_model.run(os.path.join(self.input_path,item))
                    trans_save_path=os.path.join(self.translate_save_path, os.path.splitext(item)[0]+"_transed.lrc")
                    self.translate_module.run(single_lrc_resu,trans_save_path)
                    # lrc_reu.append(single_lrc_resu)
            #translate and gennerate lrc
        else:
            raise Exception("invalid funcMode")