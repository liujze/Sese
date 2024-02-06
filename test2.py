from core.transcribe import SeseTranscribe
from core.translate import SeseTranslate
import os
import yaml
with open("config.yaml",encoding="utf-8") as fp:
    config=yaml.safe_load(fp)
obj=SeseTranscribe(config)
a=obj.RestoreLrcFile("./music/02.ドスケベ尋問開始.lrc")
b=obj.merge_redundant_senten(a)
b=obj.merge_timegap(b)

translate_module=SeseTranslate(config)
translate_module.run(b,"temp_cn.lrc")
# with open("test.lrc","w",encoding="utf-8") as fp:
#     for item in b:
#         tic=obj.format_time(item[0])
#         fp.write("%s %s\n"%(tic,item[1]))
# obj.save_to_lrc(b,"test.lrc")

