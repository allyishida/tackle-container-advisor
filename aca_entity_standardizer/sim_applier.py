# *****************************************************************
# Copyright IBM Corporation 2021
# Licensed under the Eclipse Public License 2.0, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# *****************************************************************

 
 
import string
import configparser
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils_nlp import  utils
from sim_utils import sim_utils

config_obj = configparser.ConfigParser()
config_obj.read("./config.ini")



class sim_applier:

    def __init__(self,model_path):
        
        self.all_instances=[]
        
        self.sim_threshold= float(config_obj["model"]["sim_threshold"])
        self.top= float(config_obj["model"]["top"])
        
        self.model_path=model_path
        self.kg_dict_csv="standardization_dict2_kg2.csv"
         
        self.model_name="standardization_vectorizer.pickle"
        self.tfidf_name="standardization_model.pickle"
        self.instances_name="standardization_dict.pickle"
        self.NA_CATEGORY="NA_CATEGORY"
        self.NA_VARIANT="NA_VARIANT"
        
        self.load_model(self.model_path)
        self.ent_scores_sim=[]
        
    def load_model(self,model_path):
           
        self.tfs = pickle.load(open(model_path+self.model_name, "rb"), encoding="utf8")
        self.tfidf=pickle.load(open(model_path+self.tfidf_name, "rb"), encoding="utf8")
        self.all_instances=pickle.load(open(model_path+self.instances_name, "rb"), encoding="utf8")
        
    
    def calc_CosineSimilarity(self,tfs_text):

        """
        Compute Cosine Similarity   
        :param tfs_text: tfs text input

        :returns: Sorted list of similarities
        :rtype: list

        """
   
        sims=[]
        matrixValue = cosine_similarity(tfs_text,self.tfs)
        id=0
        for  each in matrixValue[0]:
            sims.append(each)
            id+=1
    
        sims_sorted = sorted(enumerate(sims), key = lambda item:-item[1])
        return sims_sorted
    

    def get_entity_standardization(self):
        """
        :returns: scores similarities
        :rtype: list
        
        """
        return self.ent_scores_sim
    
  
    def remove_duplicate_category(self,old_list):
        """
        Remove duplicate from list 

        :param old_list: List of categories

        :returns:  A new list with no duplicate categories
        :rtype: list

        """
 
        list1 = []
        category_list=[]
         
        for  element in old_list: 
            sim_id_, sim=element
             
            category,variant,keywords=self.all_instances[sim_id_]
            if (category.strip() not in category_list):
                list1.append(element)
                category_list.append(category.strip())
        
        return list1
    
    
    def entity_standardization(self,id_, text): 
        """
        Standardize entities. An entity represent a technology( OS ,APPS , APP SERVERS ,LIBS , LANG or RUNTIMES)

        :param text: Entity to standardize
        :type text: string

        
        :returns: List of Similarities with the associated similarity score values
        :rtype:  list

        """
      
        text1=utils.input_preprocess(text)
        
        query=utils.my_tokenization0(text1.strip().lower())
                
        score=[]
        if query==" " or query=="":
            return score
        
        sims=[]
        if len(query)>0:
            tfs_text=self.tfidf.transform([text1])
            sims=self.calc_CosineSimilarity(tfs_text)
            if len(sims)>0:
                i=0
                
                sims1=self.remove_duplicate_category(sims)
                
                while i <self.top:
                    sim_id_,similarity=sims1[i]
                
                    if similarity<=self.sim_threshold:
                        score.append([id_, text,self.NA_CATEGORY, self.NA_VARIANT,0])
                        break
                    
                    category,variant,keywords=self.all_instances[sim_id_]
                    score.append([id_, text,category, keywords,similarity])
 
                    i+=1
        return score
    
    
    def tech_stack_standardization(self,tech_stack):

        """
        Standardize Tech Stack.Tech_stack may include OS ,APPS , APP SERVERS ,LIBS , LANG or RUNTIMES
        
        
        :param tech_stack: A String input text made of all Techs.Example input: "Windows, WebSphere App Server"
        :type tech_stack: string

        :returns: list of Entities with the highest similarity score for each entity
        :rtype: list
        """

      
        id_=0
        text0 = tech_stack
        tech_list0=text0.split(",")
        tech_list0=utils.remove_duplicate(tech_list0)
        tech_list=[]
        
        for each in tech_list0:
            if utils.remove_noise_snippet(each):
                continue
            sublist=utils.split_subtext(each)
            for sub_each in sublist:
                tech_list.append(sub_each)

        tech_scores_sim=[]        
        tech_list0=tech_list
        tech_list=utils.remove_duplicate(tech_list)
        
        
        for each in tech_list:            
            if each=="" or each==" " or each=="  " or each.isdigit():
                continue
            
            if utils.remove_noise_snippet(each):
                continue
            
            if each!="":
                scores=self.entity_standardization(id_,each) 
                
                for each in scores:
                    id_,query_text,category,keywords,max_sim=each
                
                    if category!=self.NA_CATEGORY:
                             
                        tech_scores_sim.append([category,max_sim])
                               
            if len(tech_scores_sim)==0:
                tech_scores_sim.append([self.NA_CATEGORY,self.sim_threshold])
            
        tech_scores_sim_final=utils.remove_duplicate_tuple(tech_scores_sim)    
        self.ent_scores_sim=tech_scores_sim_final     
        return  self.ent_scores_sim
    
 
    def detect_entity_snippet(self,text):

        """
        Detect Snippet
        
        
        :param text:
        :type text:

        :returns: 
        :rtype: list  

        """
        words= utils.my_tokenization0(text)
        entity_list=[]
        id_=0
        
        for each_word in words:
            if each_word.isdigit():
                continue
            
            cur_scores=self.entity_standardization(id_,each_word)
            if len(cur_scores)>0:
                    id_,query_text,category,keywords,max_sim=cur_scores[0]
                
                    if max_sim>float(config_obj["model"]["max_sim"]) and category!=self.NA_CATEGORY:
                        entity_list.append([id_, each_word,category, max_sim])
                    else:
                        entity_list.append([id_, each_word,"TBD", 0])   
            else:
                entity_list.append([id_, each_word,"TBD", 0])   
                
            id_+=1
            
        return entity_list