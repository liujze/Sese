#encoding:utf-8
import os
import httpx
from openai import OpenAI
from concurrent.futures import ThreadPoolExecutor,as_completed

import re



class SeseTranslate():
    def __init__(self,config) -> None:
        self.isdebug=config["isdebug"]
        if(config["translate"]["transmode"]=="gpt"):
            print("[***]using gpt to translate")
            os.environ['OPENAI_API_KEY'] = config["translate"]["transapi"]
            proxies=None
            if(config["proxy"]["isproxy"]):
                print("[***]set proxy:%s:%s"%(config["proxy"]["proxy_ip"],config["proxy"]["proxy_port"]))
                addr="%s:%s"%(config["proxy"]["proxy_ip"],config["proxy"]["proxy_port"])
                proxies={
                    'http://': addr,
                    'https://': addr
                }
            self.client = OpenAI(base_url=f"https://api.chatanywhere.tech/v1", http_client=httpx.Client(proxies=proxies))
            self.prompt=config["translate"]["prompt"]
            self.commit_freq = config["translate"]["commit_freq"]
            self.max_thread_num = config["translate"]["max_thread_num"]
                
    def run(self,text_list, trans_save_path, process_video=False):
        
        if(isinstance(text_list, str)):
            resu=self.get_response(text_list)
        elif(isinstance(text_list,list)):
            # 线程池处理
            with ThreadPoolExecutor(max_workers=self.max_thread_num) as executor:
                merge_text_list=[]
                merge_text=""
                time_list=[]
                for index,tim_text in enumerate(text_list):
                    if(process_video==False):
                        tim,text=tim_text
                        time_list.append(tim)
                    else:
                        tim,text,tim_en=tim_text
                        time_list.append((tim,tim_en))
                    if((index+1)%self.commit_freq==0):
                        # self.get_response(merge_text)
                        merge_text+="[%d] %s"%(index+1,text)
                        merge_text_list.append(merge_text)
                        merge_text=""
                    else:
                        merge_text+="[%d] %s\n"%(index+1,text)
                if( merge_text!=""):
                    merge_text_list.append(merge_text[:-2])
                self.save_list_as_log(merge_text_list,"1.log")

                
                if(1):
                    futures = [executor.submit(self.get_response, item) for item in merge_text_list]
                    # import pdb;pdb.set_trace()
                    #debug 暂时存储到一个txt文件
                    trans_resu=[]
                    for future in as_completed(futures):
                        tempresu = future.result() 
                        split_tempresu=tempresu.split("\n")
                        if(self.commit_freq>len(split_tempresu)):
                            split_tempresu=self.lineNum_exception_handle(split_tempresu)
                        #TODO 存在另一种异常情况，函数大于期望行数
                        trans_resu+=split_tempresu
                else:
                    #debug 单线程代码
                    trans_resu=[]
                    for item in merge_text_list:
                        tempresu=self.get_response(item)
                        split_tempresu=tempresu.split("\n")
                        if(self.commit_freq!=len(split_tempresu)):
                            split_tempresu=self.lineNum_exception_handle(split_tempresu)
                        trans_resu+=split_tempresu
                if(process_video==False):
                    self.save_lrc(time_list,trans_resu,trans_save_path)
                else:
                    self.save_srt(time_list,trans_resu,trans_save_path)
                resu=trans_resu
        return resu
        
    def create_messages(self, text_list):
        messages = [
            {'role': 'system',
            'content': self.prompt},
            {'role': 'user', 'content': text_list},
        ]
        return messages
    
    def get_response(self, request_str):
        message=self.create_messages(request_str)
        try:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=message
                )
            #处理响应
            if(self.isdebug):
                print("[***]get response",completion)
            result=self.process_response(completion)
            
        except Exception as e:
            raise Exception(f"Chatgpt Error: {str(e)}")
        return result
    
    
    def process_response(self,response):
        vail_data = None
        try:
            if response.choices:
                result = response.choices[0].message.content.strip()
                return result
            elif response.data and response.data['choices']:
                result = response.data['choices'][0]['message']['content'].strip()
                return result
            msg=f'chatGPT error:{response}'

            raise Exception(msg)
        except Exception as e:
            raise Exception(f'[error] {str(e)}')
    
    def save_lrc(self,time_list, text_list,trans_save_path):
        with open(trans_save_path, "w", encoding="utf-8") as lrc_file:
            #处理翻译字段，先转成{行号：内容}的字典
            trans_dic={}
            for item in text_list:
                pos=item.find(']')
                key=item[item.find('[')+1:pos]
                try:
                    trans_dic[int(key)]=item[pos+1:]
                except Exception as e:
                    # raise Exception(f"translated content has error lineNum: {str(item)}")
                    print(f"translated content has error lineNum: {str(item)}") #仅打印错误翻译，不做处理
            
            #写入lrc文件
            for index,tim in enumerate(time_list):
                lineNum=int(index+1)
                if lineNum in trans_dic:
                    timetick=self.format_time(tim)
                    lrc_file.write(f"%s %s\n" % (timetick,  trans_dic[index+1]))
                else:
                    timetick=self.format_time(tim)
                    lrc_file.write(f"%s \n"% (timetick))
    
    def save_srt(self,time_list, text_list,trans_save_path):
        with open(trans_save_path, "w", encoding="utf-8") as srt_file:
            #处理翻译字段，先转成{行号：内容}的字典
            trans_dic={}
            for item in text_list:
                pos=item.find(']')
                key=item[item.find('[')+1:pos]
                try:
                    trans_dic[int(key)]=item[pos+1:]
                except Exception as e:
                    # raise Exception(f"translated content has error lineNum: {str(item)}")
                    print(f"translated content has error lineNum: {str(item)}") #仅打印错误翻译，不做处理
            
            #写入srt文件
            for index,tim in enumerate(time_list):
                tim_st,tim_en=tim
                lineNum=int(index+1)
                if lineNum in trans_dic:
                    timetick_st=self.seconds_to_srt_format(tim_st)
                    timetick_en=self.seconds_to_srt_format(tim_en)
                    srt_file.write(lineNum+'\n')
                    
                    srt_file.write(f"%s --> %s\n" % (timetick_st,  timetick_en))
                    srt_file.write("%s\n\n"%trans_dic[index+1])
                else:
                    pass
    
    def seconds_to_srt_format(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        milliseconds = int((seconds % 1) * 1000)
        
        srt_format = "{:02d}:{:02d}:{:02d},{:03d}".format(hours, minutes, seconds, milliseconds)
        
        return srt_format

    def srt_to_seconds(self, srt_time):
        pattern = r"(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2}),(?P<milliseconds>\d{3})"
        parts = re.match(pattern, srt_time)
        
        if parts is None:
            return 0

        hours = int(parts.group('hours'))
        minutes = int(parts.group('minutes')) 
        seconds = int(parts.group('seconds'))
        milliseconds = int(parts.group('milliseconds'))

        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000

        return total_seconds
    
    def srt_reverse(self,srt_path):
        with open(srt_path,"r") as fp:
            srt_text=fp.read()
        results = []
        pattern = re.compile(r"(?P<start>\d{2}:\d{2}:\d{2},\d{3}) --> (?P<end>\d{2}:\d{2}:\d{2},\d{3})\n(?P<text>.+)", re.MULTILINE | re.DOTALL)
        for m in re.finditer(pattern, srt_text):
            start = m.group('start')
            end = m.group('end')
            text = m.group('text').strip()
            results.append((start, text, end))
        return results

    def format_time(self, seconds):
        # 将秒转换为 LRC 文件中使用的时间格式 [mm:ss.xx]
        m, s = divmod(seconds, 60)
        ms = int((s - int(s)) * 100)
        return '[{:02}:{:02}.{:02}]'.format(int(m), int(s), ms)

    def save_list_as_log(self, data, log_file):
        with open(log_file,'w',encoding="utf-8") as fp:
            fp.write("[by AI]\n")
            for item in data:
                fp.write("%s\n"%item)

    def lineNum_exception_handle(self, resu_list):
        #异常处理方案1 只处理句子中包含两个及以上行号的item
        after_handle_list=[]
        for item in resu_list:
            pattern = r'\[\d+\]'
            matches = re.finditer(pattern, item)
            positions = [match.start() for match in matches]
            if(len(positions)>=2):
                start=0
                split_error_item_list=[]
                for pos in positions[1:]:
                    split_error_item_list.append(item[start:pos])
                    start=pos
                split_error_item_list.append(item[start:])
                after_handle_list+=split_error_item_list
            else:
                after_handle_list+=[item]
        
        if(self.commit_freq!=len(after_handle_list)):
            #TODO 合并后按行号分割
            pass
        return after_handle_list
    
    