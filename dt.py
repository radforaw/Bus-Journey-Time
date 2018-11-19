
import requests
import shelve
import sys
	
class rcache():
	def __init__(self,name='test.db'):
		self.cache=shelve.open(name)
	
	def get(self,url,nc=False):
		if url in self.cache and nc==False:
			return self.cache[url]
		else:
			print (url,'***')
			a= False
			tries=5
			while a==False and tries>0:
				try:
					a=requests.get(url,timeout=20)
					#print (a.content)
					#sys.exit(0)
				except:
					print('retry')
					tries-=1
			if nc==True:
				return a.content
			self.cache[url]=a.content
			return self.cache[url]
	
	def cls(self):
		self.cache.close()
	
		
