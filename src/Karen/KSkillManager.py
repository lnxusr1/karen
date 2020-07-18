'''
Project Karen: Synthetic Human
Created on Jul 12, 2020

@author: lnxusr1
@license: MIT Lincense
@summary: Skill and Skill Manager classes for learned skills

'''

import os, logging, random
from padatious import IntentContainer
from .KShared import dayPart

class SkillManager:
    """Translates text commands into skill results."""
    
    def __init__(self, brain_obj=None):
        self._name = "SKILLMANAGER"
        self.skill_folder = ""
        self.brain = brain_obj
        
        self.skills = []

    def initialize(self):
        
        logging.debug(self._name + " - Initalizing")
        
        self.intentParser = IntentContainer('/tmp/intent_cache')

        d = os.path.join(os.path.dirname(__file__), "skills")
        skillModules = [os.path.join(d, o) for o in os.listdir(d) 
                    if os.path.isdir(os.path.join(d,o))]
        
        for f in skillModules:
            mySkillName = os.path.basename(f)
            logging.debug(self._name + " - Loading " + mySkillName) 
            mySkillModule = __import__(mySkillName)
            mySkillClass = mySkillModule.create_skill()
            mySkillClass.brain = self.brain
            mySkillClass.initialize()
            
        #print(self.skills)
        logging.debug(self._name + " - Skills load is complete.")
        
        self.intentParser.train(False) # False = be quiet and don't print messages to stdout

        logging.debug(self._name + " - Training completed.")

        logging.debug(self._name + " - Initalization completed.")
        
        
        #print(container.calc_intents('Hello there!'))
        #print(container.calc_intent('Search for cats on CatTube.'))
        #container.remove_intent('goodbye')

        
    def parseInput(self, text):

        try:
            intent = self.intentParser.calc_intent(text)
            #print(intent)
            # I need to be at least 60% likely to be correct before I try to process the request.
            if intent.conf >= 0.6:
                for s in self.skills:
                    if intent.name == s["intent_file"]:
                        s["callback"](intent)
                        return { "error": False, "message": "Skill completed successfully." }
            else:
                return { "error": True, "message": "Intent not understood." }
        except Exception as e:
            logging.debug(self._name + " - " + str(e))
            return { "error": True, "message": "Error occurred in processing." }

        return { "error": True, "message": "Unable to process input."}
    
    def stop(self):
        if (self.skills is not None and len(self.skills) > 0):
            for s in self.skills:
                try:
                    s["object"].stop()
                except:
                    pass

        return True
    
class Skill:
        
    def __init__(self):
        self._name = "Learned Skill"
        self.brain = None 
        
    def getMessageFromDialog(self, dialog_file, **args):
        text = ""
        df = os.path.join(os.path.dirname(__file__), "skills", self.__class__.__name__, "vocab", "en_us", dialog_file)
        
        if os.path.exists(df):
            with open(df,"r") as s:
                m=s.readlines()
                l=[]
                for i in range(0,len(m)-1):
                    x=m[i]
                    z=len(x)
                    a=x[:z-1]
                    l.append(a)
                l.append(m[i+1])
                text=random.choice(l)
                    
            if ("*dayPart*" in text):
                text = text.replace("*dayPart*", dayPart())
            
            return text
        else:
            return ""

    def initialize(self):
        return True
        
    def register_intent_file(self, filename, callback):
        fldr = os.path.join(os.path.dirname(__file__), "skills", self.__class__.__name__)
        if os.path.exists(fldr):
            if os.path.exists(fldr):
                if self.brain is not None:
                    self.brain.skill_manager.intentParser.load_file(filename, os.path.join(fldr,"vocab","en_us",filename), reload_cache=True)
                    self.brain.skill_manager.skills.append({ "intent_file": filename, "callback": callback, "object": self })
                else:
                    logging.debug(self._name + " - BRAIN not referenced")
            else:
                logging.debug(self._name + " - Error registering intent file")
        else:
            logging.debug(self._name + " - Intent file not found")
            return False
        
        return True
    
    def say(self, text):
        
        if self.brain is not None:
            return self.brain.say(text)
        else:
            logging.debug(self._name + " - BRAIN not referenced")

        return { "error": True, "message": "Error in Say command" }

    def stop(self):
        return True