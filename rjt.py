#! python3

import requests
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
import sys
fileloc='/home/ubuntu/website/website/yourapp/static/'

fileloc=''

quick={'Holloway Circus (inbound)':(43000305101,43000203501)}

routes={'Holloway Circus (inbound)':(43000305101,43000203501),'Five Ways (inbound)':(43000301102,43000207202),'Spring Hill (inbound)':(43000286602,43000207202),'St Chads (inbound)':(43000270404,43000208501),'Dartmouth Circus (inbound)':(43000253404,43000207601),'Curzon Circus (inbound)':(43000241402,43002104401),'Garrison Circus (inbound)':(43000236202,43000211304),'Bordesley Circus (inbound)':(43000230203,43000202203),'Camp Hill Circus (inbound)':(43000220102,43000211304),'Bradford Street -  Markets (inbound)':(43000218202,43000202301),'Belgrave Interchange (inbound)':(43000343202,43000203902)}

back={'harborne (outbound)':(43000205601,43000305201),'Five Ways (outbound)':(43000205601,43003003501),'Spring Hill (outbound)':(43000205601,43002870101),'St Chads (outbound)':(43000207205,43000276301),'Dartmouth (outbound)':(43000252102,43000253601),'Curzon (outbound)':(43002104402,43000241502),'Garrison (outbound)':(43000212601,43000236402),'Camp Hill (outbound)':(43000211501,43000220201),'Bordesley (outbound)':(43000211502,43000230302),'Moseley (outbound)':(43002103506,43000218101),'Pershore (outbound)':(43000213202,43000343201)}

thresh=1.2

def inseconds(tmp):
	tmp=tmp.split(':')
	return float((int(tmp[1])*60)+int(tmp[2]))
	
def getdata(route,day=0):

	n=datetime.timedelta(days=day)
	dy=datetime.datetime.now()-n
	dys=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	#print (dys[dy.weekday()])
	tm=dy.strftime('%Y-%m-%d')
	#print (tm)
	
	url='https://realjourneytime.azurewebsites.net/index.php?method=Journeys&fromCode='+str(route[0])+'&toCode='+str(route[1])+'&dateString='+tm
	#print (url)
	a= False
	tries=5
	while a==False and tries>0:
		try:
			a=requests.get(url,timeout=20)
		except:
			print('retry')
			tries-=1
	if a==False:
		return False
	try:
		r=json.loads(a.content)
	except:
		return False


	res=[]
	for n in r[u'JourneyTimes']:
		res.append([n[u'ScheduledDepartureTime'],inseconds(n[u'ScheduledJourneyTime']),inseconds(n[u'RealJourneyTime']),n[u'RealDepartureTime'],dys[dy.weekday()]])
	return res

def quickyaynay(res):
	if len(res)==0:
		return False
	retval=[a[2]/a[1] for a in res[-5:]]
	print ([a[2]/a[1] for a in res])
	#pri
	return sum([a>thresh for a in retval])
	
def totalday(res,ct):
	if len(res)==0:
		return 0
	retval=[(a[2]/a[1])>thresh for a in res]
	s=sorted([a[2]/a[1]for a in res])[int(len(res)*.85)]
	j=[[datetime.datetime.strptime(a[3],'%Y-%m-%dT%H:%M:%S').time(),(a[2]/a[1])>thresh] for a in res]
	k=[a[0].hour+a[0].minute/60.0 for a in j if a[1]]
	m=[a[0].hour+a[0].minute/60.0 for a in j if not a[1]]
	size=[(a[2]/a[1])*64 for a in res if (a[2]/a[1])>thresh]
	#print ([a[1] for a in res])

	plt.scatter([a for a in k],[ct for n in range(len(k))],c='red',marker='d',s=size,edgecolors='face')
	plt.scatter([a for a in m],[ct for n in range(len(m))],c='blue',edgecolors='face')
	return (float(sum(retval))/len(res))*100,s

def drawgraph(res):
	retval=[a[2]/a[1] for a in res]
	cols=['yellow' if a[2]/a[1]<0.9 else 'green' if 0.9<a[2]/a[1]<1.1 else 'red' for a in res]
	times=[a[0].split('T')[1][:5] for a in res]

	plt.bar(range(len(res)),[a[2] for a in res],color=cols)
	plt.plot(range(len(res)),[a[1] for a in res],color='blue',linewidth=4)
	plt.xticks(range(len(res)), times,rotation=60)
	plt.show()
	return retval

def cumulativedelayminutes(res):
	if len(res)==0:
		return 0
	print (datetime.datetime.strptime(res[0][3],'%Y-%m-%dT%H:%M:%S').date())
	print (sum([a[2]-a[1] if a[2]-a[1]>=0 else 0 for a in res])/60)
	return sum([a[2]-a[1] if a[2]-a[1]>=0 else 0 for a in res])/60

if __name__=='__main__':
	import time
	while True:
		plt.style.use('ggplot')
		#print ("is it fucked?")

		#a=getdata(back['const hill']
		ct=1
		g2=[]
		for n in quick:
			for j in range(40):#[30,23,16,9,2]:
				a=getdata(quick[n],day=j)
				if a==False:
					continue
				print (n,quickyaynay(a),totalday(a,ct))#datetime.datetime.strptime(a[-1][3],'%Y-%m-%dT%H:%M:%S'),a[-1][3])
				try:
					g2.append([a[0][4],cumulativedelayminutes(a)])
				except:
					pass
				ct+=1
				time.sleep(1)
			ct=1
			plt.title(n+"\nUpdated "+str(datetime.datetime.now()))
			x1,x2,y1,y2 = plt.axis()
			plt.axis((5,24,y1,y2))
			plt.xlabel('Hour Starting')
			plt.ylabel('Days')
			plt.savefig(fileloc+'bus.png')
			#plt.show()
			plt.close()
			g2.reverse()
			plt.bar(range(len(g2)),[b[1] for b in g2])
			plt.xticks(range(len(g2)),[a[0] for a in g2],rotation=45)
			plt.title(n+" Bus Delays\nUpdated "+str(datetime.datetime.now()))
			plt.xlabel('Day')
			plt.ylabel('Delay minutes')
			plt.savefig(fileloc+"busdelay.png")
		time.sleep(900)

# how many times 10% above threshold
# maximum delay
# incident lemgth - sustained over 10%
