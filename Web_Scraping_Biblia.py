import re
import sys
import requests
import pandas as pd
from time import time
from bs4 import BeautifulSoup
#############################
def dif_time(start_time):
	t=time()-start_time
	m=int(t/60)
	s=t - m*60
	print( "--- {}:{:.3f} ---".format(m,s) )
#############################
##Baixar o html do site:
list_version=['nvi','nvt','ara','naa','acf','arc','tb','vc','akjv']
idx=int(sys.argv[1])
#idx=0
version=list_version[idx]

url='https://www.bibliaonline.com.br/'+version+'/'
site=requests.get(url).content
soup=BeautifulSoup(site, 'html.parser')

print(f'Versão {version.upper()}')
#############################
start=time()

#Obter lista de livros (abreviados) e lista de nome dos livros:
Livros=[]; Livros_name=[]; gn=False
for a in soup.find_all('a', href=True):
	if 'gn' in a.get('href'): gn=True;
	if gn==True:
		Livros.append(a.get('href').split('/')[-1])
		Livros_name.append(a.get_text())

print(f'   66 livros: {len(Livros)==66}')
if len(Livros)!=66: quit()

#############################
#Obter lista com o número de capítulos de cada livro:
Cap=[]
for link in [url+l for l in Livros]:
	site=requests.get(link).content
	soup=BeautifulSoup(site, 'html.parser')
	href=[]
	for a in soup.find_all('a', href=True):
		last=a.get('href').split('/')[-1]
		if last.isnumeric():
			href.append(last)
	Cap.append(len(href))

dif_time(start)
#--- 0:17.133 ---
#############################
#Obter lista com os versículos de cada capítulo de cada livro:
#n_vers_cap  -> lista temporária com o número de vers de cada cap de um livro específico;
#n_vers_list -> lista com o número de vers de cada cap de cada livro;
#tag_class_v -> tags que contém os vers (texto);
#Vers_Cap    -> lista temporária com os vers de um cap específico;
#Vers_Livro  -> lista temporária com os vers de um livro específico;
#Vers_Biblia -> lista (de listas) com todos os vers (de cada cap de cada livro);

start=time()

Vers_Biblia=[]
n_vers_list=[]
for id_l in range(len(Livros)):
	print(Livros[id_l])
	Vers_Livro=[]
	n_vers_cap=[]
	for c in range(1,Cap[id_l]+1):
		link=url+Livros[id_l]+'/'+str(c)
		site=requests.get(link).content
		soup=BeautifulSoup(site, 'html.parser')
		Vers_Cap=[]
		tag_class_v=soup.find_all('p', class_="jss43")
		n_vers_cap.append( len(tag_class_v) )
		for tag_v in tag_class_v:
			Vers_Cap.append( tag_v.get_text().split(' ',1)[1] )
		Vers_Livro.append(Vers_Cap)
	n_vers_list.append(n_vers_cap)
	Vers_Biblia.append(Vers_Livro)

dif_time(start)
#--- 5:38.826 ---
#############################
#Criar DataFrame a partir de lista de atributos:
Lista=[]
for id_l in range(len(Livros)):
	if id_l<39:	Testamento='AT'
	else: Testamento='NT'
	for c in range(Cap[id_l]):
		for v in range(len(Vers_Biblia[id_l][c])):
			vers=Vers_Biblia[id_l][c][v]
			Lista.append( [Testamento,Livros_name[id_l],Livros[id_l],c+1,v+1,vers] )


df = pd.DataFrame(Lista,
				  columns=['testamento','livro_name','livro','n_cap','n_vers','vers'])

df = df.astype(dtype= { 'testamento':'object','livro_name':'object','livro':'object',
						'n_cap':'int64','n_vers':'int64','vers':'object'})

df.to_csv('Vers_Biblia_'+version+'.csv')
#############################