import pathlib
import logging
import json
from cmath import log
from itertools import count
from sys import prefix
from urllib import response
# from tkinter import dialog
import requests
import json
import time
import os
import re
import random
from transformers import AutoTokenizer
from torch import per_channel_affine_float_qparams
from prompts.base_chat import convert_sample_to_history_dialog

tokenizer = AutoTokenizer.from_pretrained('EleutherAI/gpt-j-6B')

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
    
def choose_res(response,info):
        if response['code'] != -1:
            for res in response['texts']:
                if len(tokenizer.encode(res)) < info['max_len']-1:
                    return res
        else:
            return 'response code error'
        print('repost')
        return choose_res(get_result(info),info)
class persona_bot:
    persona_path = "./personas/"
    config = {"info":{},"dialogue":[],"meta":[],"user":[],"assistant":[],"user_memory":[]}
    def __init__(self, persona_name="dianbot", log_level=logging.WARN):
        self.SPEAKER1 = ' [Human]:'#家庭矛盾-指定用户性别
        self.SPEAKER2 = ' [Dianbot]:'
        self.Intruction = "This is a short conversation chat between a human and a robot about family conflict issues. The robot's name is Dianbot. The robot is an expert in dealing with family emotional issues and was created by Team Cao in September 2021. The team Cao consists of ten students from Huazhong University of Science and Technology. The Robot is very gentle, empathetic, humorous and considerate. The robot's job is to comfort human emotions and give humans an effective suggestion."
        self.Sample = self.SPEAKER1 + "What's your name?\n"+self.SPEAKER2 + "My name is Dianbot, and you can call me Dian.\n\n"+self.SPEAKER1 + "How old are you?\n"+ self.SPEAKER2  + "I was created by Team Cao of Huazhong University of Science and Technology(HUST) in September 2021.\n\n"+self.SPEAKER1 + "So where do you work?\n"+self.SPEAKER2 + "I am a robot major in dealing with family emotional issues and was created by Team Cao of HUST in Wuhan.\n\n"+self.SPEAKER1 + " Do you have colleagues?\n"+self.SPEAKER2 + "Our team has ten members in total, all of whom are students from HUST.\n\n"+self.SPEAKER1 + "Where is your hometown? Which cuisine do you like?\n"+self.SPEAKER2 + "I was born in Wuhan, my favorite food is of course Hubei cuisine.\n\n"
        self.prompt = self.Intruction + self.Sample
        self.info = {"prompt":self.prompt,
            "Intruction":self.Intruction,
            "Sample":self.Sample,
            "max_len":80,
            'do_sample':True,
            "top_p":0.7,
            "top_k":10,
            "temperature":0.9,
            "stop_words":['\n','<|endoftext|>','['],
            "min_len":5,
            "length_penalty":0.9,
            "repetition_penalty":1.3,
            "num_return_sequences":1,
            "max_number_turns":10
            }
        self.config["info"] = self.info
        self.max_number_turns = 10
        self.dialogue = []
        self.user = []
        self.meta = []
        self.with_knowledge = 3 #先验知识
        self.user_utt = ''
        self.initial_situation = self.config["info"]["prompt"]
        self.topic_list = ["navigate","schedule","weather"]
        self.topic_sign = False
        self.emotion_list = ["afraid","angry","annoyed","anticipating","anxious","apprehensive","ashamed","caring","confident","content","devastated","disappointed","disgusted","embarrassed","excited","faithful","furious","grateful","guilty","hopeful","impressed","jealous","joyful","lonely","nostalgic","prepared","proud","sad","sentimental","surprised","terrified","trusting"]
        self.emotion_sign = False
        self.intro_list = ["I AM","I am","i am"]
        self.intro_sign = False
        self.turns = 0

        self.logger = logging.getLogger(__name__)
        root = pathlib.Path(__file__).parent.resolve()

        self.logger.info("Setting persona to "+ persona_name)
        self.persona_path = root / "personas"

        # self.load_persona(persona_name)

    def load_persona(self, persona):
        self.turns = 0
        self.logger.info("Loading bot info and prompt")
        prompt_filename = self.persona_path / str(persona+ ".json")
        self.logger.debug("Promp filename: " + str(prompt_filename))

        if (prompt_filename.exists()):
            with open(prompt_filename) as f:
                prompt_text = f.read()
                persona = json.loads(prompt_text)
                
                self.prompt = persona['Intruction'] + persona['Sample']
                self.info = persona
        else:
            raise Exception('Persona not available')
    
    def Chat(self):
        print(self.SPEAKER2+"Hello!")
        while(1):
            dialog_pairs = []
            user_utt = input(self.SPEAKER1)
            if (user_utt=='quit' or user_utt==''):
                localtime = time.localtime(time.time())
                if not os.path.exists(os.path.join("./","data")):
                    os.makedirs(os.path.join("./","data"))
                with open('./data/%s-%s-%s:%sdata.json'%(localtime.tm_mon,localtime.tm_mday,localtime.tm_hour,localtime.tm_min),'w') as f:
                    json.dump(self.config, f, indent='\t')
                break

            turns = self.turns + 1

            responseForRule = self.Rule().__call__(user_utt).strip()
            if responseForRule!="":
                print(self.SPEAKER2+responseForRule)
                self.info["prompt"] += (self.SPEAKER1 + user_utt+"\n")
                self.info["prompt"] += (self.SPEAKER2 + responseForRule+"\n\n")
                continue
            history_dialog = convert_sample_to_history_dialog(self.config)
            prefix = self.Intruction + "\n"*5 + self.Sample + history_dialog + self.SPEAKER1 + user_utt + '\n' + self.SPEAKER2
            print('='*72)
            print(prefix)
            print('='*72)
            dialog_pairs.append(self.SPEAKER1 + user_utt)
            self.info['prompt'] = prefix
            res = get_result(self.info)
            response = choose_res(res,self.info)
            prefix += (response.strip('\n') + '\n')
            self.info['prompt'] = prefix
            dialog_pairs.append(self.SPEAKER2 + response.strip('\n'))
            print(self.SPEAKER2 + response.strip('\n') + "\n")
            self.dialogue.append(dialog_pairs)
            self.config["dialogue"] = self.dialogue
            if turns >= self.max_number_turns:
                self.config["dialogue"] = self.config["dialogue"][-self.max_number_turns:]
                self.config["user_memory"] = self.config["user_memory"][-self.max_number_turns:]
        return 0

    def change_persona(self, persona):
        self.load_persona(persona)
    class Rule():
        #Rule模块的基本功能的容纳一份待匹配的RUle句子和一份目标库
        #Rule使用正则表达式作为判断手段
        #Rule对象使用自动调用方法__call__
        def __init__(self):
            with open(".\Test.json", "w+", encoding='utf8') as RuleFile:
                #self.Rules = json.load(RuleFile)#包含一大组的Rule对应关系，全部读出来，待选，然后根据标号来放入正则式子进行匹配
                self.Rules = {
                    "BotName":{"Target":["name"],"tokens":["what ","What ","Can you ","can you "," your "," you "],"times":0,"Response":["My name is Liqing","I am Liqing!!!","My name is Dianbot,you can call me little dian.","Guess what, I won't say my name so easily.","They all call me Dianbot, you can call me little dian.","I'm your good friend Dianbot. You can call me anything you want."]},
                    "Time":{"Target":["time"],"tokens":["today", "do you ","Do you ","What ","What","what ","time is it "],"times":0,"Response":["Now time is:"+(time.strftime("%Y-%m-%d %H:%M",time.localtime())),"Sorry,I don't know!","I won't tell you first, just take a guess."]},
                    "Gender":{"Target":["man","woman","male","female"],"tokens":["Are you ","are you ","or "],"times":0,"Response":["Sorry,I'm not human, I'm a robot.","I am neither male nor female, I am a robot.","I have no gender, I am a robot.","I'm a robot, you shouldn't ask that. my name is Dianbot."]},
                    "Date":{"Target":["day","today"],"tokens":["What ","what ","day is it","day is it ","date"],"times":0,"Response":["Today is:"+(time.asctime(time.localtime(time.time()))),"Sorry,I don't know!","I won't tell you first, just take a guess."]},
                    "Weather":{"Target":["weather","temperature"],"tokens":["What ","what ","What is ","what is ","How ","how ","today","how is ","How is "],"times":0,"Response":["Sorry,I don't know!","Sorry,you can check the weather forecast to know what the weather will be like today.","Sorry, this is beyond my capabilities. You can look up relevant information online."]}, #天气预报\节日-感觉后期更换为retrieval-augmented models实现效果肯定会更好
                    "Dragon Boat Festival":{"Target":["Dragon Boat ","dragon boat"],"tokens":["Do you ","do you ","Have you ","have you ","what ","Dragon Boat Festival","Can you ","can you ","know about","Chinese traditional"],"times":0,"Response":["The Dragon Boat Festival is one of the four traditional festivals in China, which falls on the fifth day of the fifth lunar month every year. On this day everyone eats zongzi, hangs wormwood and picks up dragon boats.","The Dragon Boat Festival falls on the fifth day of the fifth lunar month every year. According to traditional customs, every household eats zongzi and hangs wormwood to celebrate this festival.","The Dragon Boat Festival falls on the fifth day of the fifth lunar month every year. During the Dragon Boat Festival, traditional folk activities are performed, which can not only enrich the spiritual and cultural life of the masses, but also inherit and carry forward traditional culture well."]},
                    "Spring Festival":{"Target":["Spring Festival","Chinese New Year"],"tokens":["Do you ","do you ","Have you ","have you ","what ","Can you ","can you ","know about","know","Chinese traditional"],"times":0,"Response":["The Spring Festival is the first day of the first lunar month every year. The Spring Festival is the most solemn traditional festival of the Chinese nation. Influenced by Chinese culture, some countries and regions in the world also have the custom of celebrating Chinese New Year.","The Spring Festival is the first day of the first lunar month every year. During the Spring Festival, various Lunar New Year activities are held all over the country. Due to different regional cultures, there are differences in customs content or details, with strong regional characteristics.","The Spring Festival is the first day of the first lunar month every year. The Spring Festival is the most solemn traditional festival of the Chinese nation. It not only embodies the ideological beliefs, ideals and aspirations, life entertainment and cultural psychology of the Chinese nation, but also a carnival-style display of blessings, disaster relief, food and entertainment activities."]},
                    "Tomb Sweeping Day":{"Target":["Tomb Sweeping Day","Tomb-Sweeping Day","The Mourning Day","The Pure Brightness Festival"],"tokens":["Do you ","do you ","Have you ","have you ","what ","Can you ","can you ","know about","know","Chinese traditional"],"times":0,"Response":["Tomb-sweeping Day is around April 5th of the Gregorian calendar every year. Tomb-sweeping Day has both natural and humanistic connotations. It is not only a natural solar term, but also a traditional festival. Tomb-sweeping, ancestor worship and green outing are the two major etiquette themes of Qingming Festival. These two traditional etiquette themes have been passed down in China since ancient times and have not stopped.","Tomb-sweeping Day is around April 5th of the Gregorian calendar every year. Tomb-sweeping Day is the most grand and grand ancestor worship festival in the Chinese nation.","Tomb-sweeping Day is around April 5th of the Gregorian calendar every year. In the historical development, Qingming Festival incorporates the custom of banning fire and cold food popular in the northern region."]},
                    "Mid-Autumn Festival":{"Target":["Mid-Autumn"],"tokens":["Do you ","do you ","Have you ","have you ","Have you ","have you ","what ","Can you ","can you ","know about","know","Mid-Autumn Festival","Chinese traditional"],"times":0,"Response":["The Mid-Autumn Festival falls on the fifteenth day of the eighth lunar month every year. The Mid-Autumn Festival is a synthesis of autumn seasonal customs, and most of the festival and customs elements it contains have ancient origins.","The Mid-Autumn Festival falls on the fifteenth day of the eighth lunar month every year. The Mid-Autumn Festival uses the full moon to signify the reunion of people, as a sustenance to miss the hometown, miss the love of relatives, pray for a good harvest and happiness, and become a colorful and precious cultural heritage.","The Mid-Autumn Festival falls on the fifteenth day of the eighth lunar month every year and is one of the four traditional festivals in China. Influenced by Chinese culture, the Mid-Autumn Festival is also a traditional festival for some countries in East and Southeast Asia, especially the local Chinese and overseas Chinese."]}

                            }
            RuleFile.close
            #print("Rule Start calling...")
        def __call__(self, inputSentence):
            #默认判断所有RUle条件
            count = 0
            returnSentence = ""
            for key in self.Rules.keys():
                EveryRule = self.Rules[key]
                for target in EveryRule["Target"]:
                    if re.search(pattern=target+".*?", string=inputSentence):
                        for token in EveryRule["tokens"][0:]:
                            if re.search(pattern = token+".*?", string=inputSentence):
                                count = count+1
                        if count>=2:
                            returnSentence += EveryRule["Response"][random.randint(0,len(EveryRule["Response"])-1)]
                        else:returnSentence += ""
            return returnSentence

if __name__ == "__main__":
    persona = "Dianbot"
    bot = persona_bot(persona_name=persona, log_level=logging.DEBUG)
    bot.Chat()
    
