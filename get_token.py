from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import string
import matplotlib.pyplot as plt
import numpy as np
import json
import math


punc_lst = "!\"$%&\'()*,-.\\:;<=>?@[]^_`{|}~0123456789" #does not include /, #, + 

general_lst = ["Python", "JavaScript", "C#", "C", "C++", "Java", "Golang", "Go", "PhP", "Kotlin", "Swift", "Rust", "Julia"]
frontend_lst = ["VueJS", "Vue", "ReactJS", "React", "HTML", "CSS", "Angular", "Bootstrap"]
backend_lst = ["Spring", "Flask", "Django", "Laravel", "Nodejs", "ASPNET", "NET"]
tools_lst = ["Azure", "AWS", "AJAX", "jQuery", "Git", "Linux","RabbitMQ", "Celery", "Ubuntu", "GCP", "Kubernetes", "Docker"]
db_lst = ["MSSQL", "MySQL", "MongoDB", "JSON", "XML", "Redis", "Memcache", "PostgreSQL", "Postgres", "DynamoDB", "MariaDB"]
gen_dic = {}
front_dic = {}
back_dic = {}
tools_dic = {}
db_dic = {}
dic_lst = [gen_dic, front_dic, back_dic, tools_dic, db_dic]
name_lst = ["general", "front", "back", "tools", "db"]
json_lst = []

def dic_init():
	for lan in general_lst:
	    gen_dic[lan] = 0
	for lan in frontend_lst:
	    front_dic[lan] = 0
	for lan in backend_lst:
	    back_dic[lan] = 0
	for lan in tools_lst:
	    tools_dic[lan] = 0
	for lan in db_lst:
	    db_dic[lan] = 0

def create_transdic(string):
	dic = {}
	for c in string:
		dic[c] = ""
	return dic

def parse_JD(url):
	"""
	Things to look out for: 
	1. Google Cloud
	"""
	driver = webdriver.Chrome("path/to/chromedriver") #chrome driver location
	print(url)
	driver.get(url)
	html = BeautifulSoup(driver.page_source, "lxml")
	job_desc = html.findAll("p", {"class": "mb-5 r3 job-description__content text-break"}) 
	job_req = html.findAll("div", {"class": "col p-0 job-requirement-table__data"})
	if len(job_desc) == 0:
		#sometimes no result 
		return
	jd = str(job_desc[-1])
	for i in range(5, len(job_req)):
		jd = jd + " "  + str(job_req[i])
	jd = jd.replace('\r\n', ' ') 
	jd = jd.replace('\n', ' ')
	jd = jd.replace('\t', '')
	punc_dic = create_transdic(punc_lst)
	transtab = str.maketrans(punc_dic)
	jd = jd.translate(transtab)
	jd_token = jd.split(" ")
	index = 0
	leng = len(jd_token)
	while index < leng:
	    #check for "/ and 、"
	    if "/" in jd_token[index] or "、" in jd_token[index]:
	        punc = ""
	        if "/" in jd_token[index]:
	            punc = "/"
	        else:
	            punc = "、"
	        new_tokens = jd_token[index].split(punc)
	        for i in range(len(new_tokens)):
	            jd_token[index] = jd_token[index].encode('ascii',errors='ignore').decode()
	            #new_tokens[i] = re.sub(r'[^\w\s]','',new_tokens[i].encode('ascii',errors='ignore').decode())#gets rid of all punctuations
	        jd_token = jd_token + new_tokens
	        jd_token = jd_token[:index] + jd_token[index+1:]
	        leng += len(new_tokens) - 1
	    else:
	        jd_token[index] = jd_token[index].encode('ascii',errors='ignore').decode()
	        #jd_token[index] = re.sub(r'[^\w\s]','',jd_token[index].encode('ascii',errors='ignore').decode())
	        index += 1
	s = set() #prevent duplicates 
	for token in jd_token:
	    for dic in dic_lst:
	        for key in dic:
	            if re.fullmatch(re.escape(key), token, re.IGNORECASE) and key not in s:
	                dic[key] += 1
	                s.add(key)
	newJson = {"url": url, "tokens": jd_token}
	json_lst.append(newJson)
	
       

def aggregate_dic():
	#general
	gen_dic["Go"] += gen_dic["Golang"]
	del gen_dic["Golang"]
	#front
	front_dic["VueJS"] += front_dic["Vue"]
	front_dic["ReactJS"] += front_dic["React"]
	del front_dic["Vue"]
	del front_dic["React"]

	#backend
	back_dic["ASP.NET"] = back_dic["ASPNET"] + back_dic["NET"]
	back_dic["Node.js"] = back_dic["Nodejs"]
	del back_dic["ASPNET"]
	del back_dic["NET"]
	del back_dic["Nodejs"]
	#tools
	tools_dic["Linux"] += tools_dic["Ubuntu"]
	del tools_dic["Ubuntu"]

	#db
	db_dic["Postgres"] += db_dic["PostgreSQL"]
	del db_dic["PostgreSQL"]


def plot_bar_x(dic, dic_name):
    # this is for plotting purpose
	name = []
	freq = []
	for lan in dic:
		name.append(lan)
		freq.append(dic[lan])
	x_pos = np.arange(len(name))
	plt.bar(name, freq)
	plt.xlabel('Language', fontsize=5)
	plt.ylabel('Count', fontsize=5)
	plt.xticks(x_pos, name, fontsize=7, rotation=30)
	yint = range(0, math.ceil(max(freq))+1)
	plt.yticks(yint)
	plt.title(dic_name)
	plt.savefig(dic_name+".png")
	plt.close()

def main():
	dic_init()
	count = 0
	with open("url.json") as f:
		urls = json.load(f)
	f.close()
	for url in urls:
		if count == 200:
			break 
		parse_JD(url['url'])
		count += 1
	with open('tokens.json', 'w') as f:
		json.dump(json_lst, f, indent=4)
	f.close()
	aggregate_dic()
	for i in range(len(dic_lst)):
		plot_bar_x(dic_lst[i], name_lst[i])
	

if __name__ == "__main__": 
	main()
