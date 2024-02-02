#encoding:utf-8
import yaml
from core.translate import SeseTranslate
mode = 2 #1 yaml /2 chatgpt

with open("config.yaml",encoding="utf-8") as fp:
    config=yaml.safe_load(fp)
print(config["transcribe"]["model_type"])

trans= SeseTranslate(config)

with open("01.lrc",encoding="utf-8") as fp:
    text=fp.readlines()

inp=[]
for line in text:
    temp=line.split(']')
    b=temp[-1][1:-1]
    a=float(temp[0].split("s")[0][1:])
    inp.append((a,b))
resu=trans.run(inp)
print(resu)


