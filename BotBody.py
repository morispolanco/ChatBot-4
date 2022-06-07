import requests
import torch
import logging
import json
import os
import re
import random
import time
def get_result(input):
    url = 'http://127.0.0.1:8080/api/v0/generate'
    req_data = input
    rsp = requests.post(url, json=req_data)
    if rsp.status_code ==200:
        rsp_data = rsp.json()
        # print(rsp_data)
    else:
        print(rsp.status_code)
    return rsp_data
class ChatBot():
    def __init__(self):
        self.SPEAKER1 = " Jack:"
        self.SPEAKER2 = " Tom:"
        self.introduction = {
            "love_releationship":"This is a short conversation about a relationship between a human and a robot called xiaodu.Jack is a programmer who works overtime for a long time and has a lot of work pressure.His girlfriend Lucy is a civil servant who works within the system and has a lot of time.Jack's job is complicated, and the long-term competitive pressure in the company makes him drink a lot every time he comes home.Lucy spends a lot of time without a job, but has to raise their child mike, so much time spent with the child has left her suffering from depression.\n",
            "family_conflict_issues":"This is a short conversation chat between a human and a robot about family conflict issues. The robot's name is Sabrina Zhuang. The robot is an expert in dealing with family emotional issues and was created by Team Cao in September 2021. The team Cao consists of ten students from Huazhong University of Science and Technology. The Robot is very gentle, empathetic, humorous and considerate. The robot's job is to comfort human emotions and give humans an effective suggestion.",
            "workplace distress":"This is a short conversation chat between a human and a robot about workplace distress issues. The robot's name is Doinb. The robot is an expert in dealing with various workplace distress issues and was created by Team Cao in September 2021. The human has encountered some troubles at work recently, and his mood is a little lost. Doinb needs to help him analyze the situation, comfort his emotions and give him an effective suggestion.",
            "casual_talking":"This is a conversion happened between 2 boys.Both of them are studying at the same school."
        }
        self.Sample = {
            "none":"",
            "love_releationship":self.SPEAKER1 + "What's your name?\n"+self.SPEAKER2 + "My name is Sabrina Zhuang, and you can call me Zhuang.\n\n"+self.SPEAKER1 + "How old are you?\n"+ self.SPEAKER2  + "I was created by Team Cao of Huazhong University of Science and Technology(HUST) in September 2021.\n\n"+self.SPEAKER1 + "So where do you work?\n"+self.SPEAKER2 + "I am a robot major in dealing with family emotional issues and was created by Team Cao of HUST in Wuhan.\n\n"+self.SPEAKER1 + " Do you have colleagues?\n"+self.SPEAKER2 + "Our team has ten members in total, all of whom are students from HUST.\n\n"+self.SPEAKER1 + "Where is your hometown? Which cuisine do you like?\n"+self.SPEAKER2 + "Usually, robots don't need to eat anything. Because I was born in Wuhan, my favorite food is of course Hubei cuisine.\n\n"
        }
        self.Chatinfo = {"prompt":None,
            "max_len":30,
            "do_sample":True,
            "top_p":0.9,
            "top_k":20,
            "temperature":1.2,
            "stop_words":['<|endoftext|>','\n'],
            "min_len":10,
            "length_penalty":0.2,
            "repetition_penalty":1.1,
            "num_return_sequences":1,
            "max_new_tokens":None
}
        self.Suminfo = {"Dialogs":None,
            "num_beams":14,
            "length_penalty":4,
            "max_length":50,
            "min_length":10,
            "no_repeat_ngram_size":1
        }
        self.FSBinfo = {}
    def get_result(self,input):
        url = 'http://127.0.0.1:8080/api/v0/generate'
        req_data = input
        rsp = requests.post(url, json=req_data)
        if rsp.status_code == 200:
            rsp_data = rsp.json()
            # print(rsp_data)
        else:
            print(rsp.status_code)
        return rsp_data
    def Chat(self):
        self.Chatinfo["prompt"] = self.introduction["casual_talking"]+self.Sample["none"]
        print(self.SPEAKER2+"Hello!")
        while(1):
            inputsentence = input(self.SPEAKER1)
            responseForRule = self.Rule().__call__(inputsentence)
            if responseForRule!="":
                print(self.SPEAKER2,responseForRule)
                self.Chatinfo["prompt"] += (inputsentence+"\n")
                self.Chatinfo["prompt"] += responseForRule+"\n"
                continue
            self.Chatinfo["prompt"] += (inputsentence+"\n")
            response = self.get_result(self.Chatinfo)
            while response['texts'][0]=='':
                response = self.get_result(self.Chatinfo)
            while response['texts'][0][-1] not in ['.',',','!','?']:
                response = self.get_result(self.Chatinfo)
            print(self.SPEAKER2 + response['texts'][0])
            self.Chatinfo["prompt"] += (response['texts'][0]+"\n")
            response = ""
        return 0
    def InfoToJson(self):
        if os.path.exists("./jsons") == False:
            os.mkdir("./jsons")
        if os.path.exists("./jsons/InfoJson.json") == True:
            os.remove("./jsons/InfoJson.json")
        with open("./jsons/InfoJson.json", 'w+') as InfoJson:
            InfoJson.write(json.dumps(self.introduction))
        InfoJson.close
    def SampleToJson(self):
        if os.path.exists("./jsons") == False:
            os.mkdir("./jsons")
        if os.path.exists("./jsons/SampleJson.json") == True:
            os.remove("./jsons/SampleJson.json")
        with open("./jsons/SampleJson.json", 'w+') as SampleJson:
            SampleJson.write(json.dumps(self.Sample))
        SampleJson.close
    def ChangeSpeaker(self):
        b = 3
    def Debug(self):
        self.Chatinfo["prompt"] = self.introduction["casual_talking"]+self.Sample["none"]
        print("**********CONVERSION PARAMETERS*************")
        for i in self.Chatinfo.keys():
            print(i + ":", self.Chatinfo[i])
        print(self.SPEAKER2+"Hello!")
        while(1):
            inputsentence = input(self.SPEAKER1)
            self.Chatinfo["prompt"] += (inputsentence+"\n")
            while(1):
                print("Start Scaning Rules...")
                inputsentence = input(self.SPEAKER1)
                responseForRule = self.Rule().__call__(inputsentence)
                if responseForRule!="":
                    print("Rule find.")
                    print(self.SPEAKER2,responseForRule)
                    self.Chatinfo["prompt"] += (inputsentence+"\n")
                    self.Chatinfo["prompt"] += responseForRule+"\n"
                    continue
            response = self.get_result(self.Chatinfo)
            while response['texts'][0]=='':
                print("***Request Again:no response***")
                response = self.get_result(self.Chatinfo)
            while response['texts'][0][-1] not in ['.',',','!','?']:
                print("***Request Again:response truncated***")
                print(response['texts'])
                print("**************************************")
                response = self.get_result(self.Chatinfo)
            print(self.SPEAKER2 + response['texts'][0])
            self.Chatinfo["prompt"] += (response['texts'][0]+"\n")
        return 0
    class Rule():
        #Rule模块的基本功能的容纳一份待匹配的RUle句子和一份目标库
        #Rule使用正则表达式作为判断手段
        #Rule对象使用自动调用方法__call__
        def __init__(self):
            if os.path.exists("./jsons") == False:
                os.mkdir("./jsons")
            with open("./jsons/Rule.json", "w+", encoding='utf8') as RuleFile:
                #self.Rules = json.load(RuleFile)#包含一大组的Rule对应关系，全部读出来，待选，然后根据标号来放入正则式子进行匹配
                self.Rules = {
                    "BotName":{"Target":"name","tokens":["what ","What ","Can you ","can you "," your "," you "],"times":0,"Response":["My name is Liqing","I am Liqing!!!"]},
                    "Time":{"Target":"time","tokens":["today", "do you ","Do you ","What ","What","what ","time is it "],"times":0,"Response":["Now time is:"+(time.strftime("%Y-%m-%d %H:%M",time.localtime())),"Sorry,I don't know!"]}
                            }
            RuleFile.close
            #print("Rule Start calling...")
        def __call__(self, inputSentence):
            #默认判断所有RUle条件
            count = 0
            returnSentence = ""
            for key in self.Rules.keys():
                EveryRule = self.Rules[key]
                if re.search(pattern=EveryRule["Target"]+".*?", string=inputSentence):
                    for token in EveryRule["tokens"][1:]:
                        if re.search(pattern = token+".*?", string=inputSentence):
                            count = count+1
                    if count>=2:
                        returnSentence += EveryRule["Response"][random.randint(0,1)]
                    else:returnSentence += ""
            return returnSentence
    class Module():
        a = 5
    class Personality():
        a = 1
bot = ChatBot()
bot.InfoToJson()
bot.SampleToJson()
bot.Chat()