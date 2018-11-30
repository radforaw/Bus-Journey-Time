
#! python3

import requests
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
import sys
import dt
import numpy as np
import csv

#fileloc='/home/ubuntu/website/website/yourapp/static/'

fileloc=''

quick={'Holloway-Circus-inbound':(43000305101,43000203501)}

routes={'Holloway-Circus-inbound':(43000305101,43000203501),'Five-Ways-inbound':(43000301102,43000207102),'Spring-Hill-inbound':(43000286602,43000207202),'St-Chads-inbound':(43000276503,43000208501),'Dartmouth-Circus-inbound':(43000253404,43000207601),'Curzon-Circus-inbound':(43000241402,43002104401),'Garrison-Circus-inbound':(43000236202,43000211304),'Bordesley-Circus-inbound':(43000230203,43000202203),'Camp-Hill-Circus-inbound':(43000220102,43000211304),'Bradford-Street----Markets-inbound':(43000218202,43000202301),'Belgrave-Interchange-inbound':(43000343202,43000203902),'harborne-outbound':(43000205601,43000305201),'Five-Ways-outbound':(43000205601,43003003501),'Spring-Hill-outbound':(43000205601,43002870101),'St-Chads-outbound':(43000207205,43000276301),'Dartmouth-outbound':(43000252102,43000253601),'Curzon-outbound':(43002104402,43000241502),'Garrison-outbound':(43000212601,43000236402),'Camp-Hill-outbound':(43000211501,43000220201),'Bordesley-outbound':(43000211502,43000230302),'Moseley-outbound':(43002103506,43000218101),'Pershore-outbound':(43000213202,43000343201)}

thresh=1.2

def inseconds(tmp):
	tmp=tmp.split(':')
	return float((int(tmp[1])*60)+int(tmp[2]))
	
def getdata(route,day=0):

	n=datetime.timedelta(days=day)
	dy=datetime.datetime.now()-n
	tf=False
	if day==0:
		tf=True
	dys=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
	tm=dy.strftime('%Y-%m-%d')	
	url='https://realjourneytime.azurewebsites.net/index.php?method=Journeys&fromCode='+str(route[0])+'&toCode='+str(route[1])+'&dateString='+tm
	l=dt.rcache()
	try:
		r=json.loads(l.get(url,nc=tf))
	except:
		return False
	finally:
		l.cls()
	#print (r)

	res=[]
	for n in r[u'JourneyTimes']:
		res.append([n[u'ScheduledDepartureTime'],inseconds(n[u'ScheduledJourneyTime']),inseconds(n[u'RealJourneyTime']),n[u'RealDepartureTime'],dys[dy.weekday()]])
	#print (res)
	return res

def periods(res):
	smooth=[(sum(res[n:n+4])/len(res[n:n+4]))>thresh+.2 for n in range(len(res)-5)]
	return simplerldecoder(smooth)
	

def simplerldecoder(data):
	flag=False
	result={}
	positioncounter=0
	currentstart=0

	for x in data:
		if x:
			if not flag:
				flag=True
				result[positioncounter]=1
				currentstart=positioncounter
			else:
				result[currentstart]+=1
		if not x and flag:
			flag=False
		positioncounter+=1
	return result

def datetimer(string):
	return datetime.datetime.strptime(string,'%Y-%m-%dT%H:%M:%SZ')

def quickyaynay(res):
	if len(res)==0:
		return False
	retval=[a[2]/a[1] for a in res[-5:]]
	print ([a[2]/a[1] for a in res])
	print(periods([a[2]/a[1] for a in res]))
	rl= periods([a[2]/a[1] for a in res])
	ret2=[]
	for j in rl:
		start=j
		finish=j+rl[j]
		if finish-start>3:
			sttime=datetimer(res[start][3])
			fintime=datetimer(res[finish][3])
			ret2.append([sttime,fintime.time(),round(((fintime-sttime).seconds/3600),1),round(sorted([n[2]/n[1] for n in res[start:finish]])[int((finish-start)*.85)],1)])
	###analyse this ^^^....
	return sum([a>thresh for a in retval]),ret2
	
def totalday(res,ct):
	if len(res)==0:
		return 0
	retval=[(a[2]/a[1])>thresh for a in res]
	s=sorted([a[2]/a[1]for a in res])[int(len(res)*.85)]
	j=[[datetime.datetime.strptime(a[3],'%Y-%m-%dT%H:%M:%SZ').time(),(a[2]/a[1])>thresh] for a in res]
	k=[a[0].hour+a[0].minute/60.0 for a in j if a[1]]
	m=[a[0].hour+a[0].minute/60.0 for a in j if not a[1]]
	size=[(((a[2]/a[1])**2)*4 )+4 for a in res if (a[2]/a[1])>thresh]
	#print ([a[1] for a in res])

	plt.scatter([a for a in k],[ct for n in range(len(k))],c='red',marker='d',s=size,edgecolors='face')
	plt.scatter([a for a in m],[ct for n in range(len(m))],c='blue',s=4,edgecolors='face')
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
	print (datetime.datetime.strptime(res[0][3],'%Y-%m-%dT%H:%M:%SZ').date())
	print (sum([a[2]-a[1] if a[2]-a[1]>=0 else 0 for a in res])/60)
	return sum([a[2]-a[1] if a[2]-a[1]>=0 else 0 for a in res])/60
	
def lastxweeks(dt,w):
	days=('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')
	ret=[]
	for n in range(7):
		for m in range(w-1,-1,-1):
			ret.append([m,days[n],(dt+datetime.timedelta(days=(n-dt.weekday())-(m*7))).date()])
		ret.append([m,'',datetime.datetime.now().date()])
	return ret


if __name__=='__main__':
	import time
	while True:
		plt.style.use('ggplot')
		#quick=routes
		summ=[]
		for n in quick:
			ct=1
			for j in range(28):#[30,23,16,9,2]:
				a=getdata(quick[n],day=j)
				if a==False:
					continue
				qyn=quickyaynay(a)
				try:
					summ+=qyn[1]
				except:
					qyn=['None']
				print (n,qyn[0],totalday(a,ct))#datetime.datetime.strptime(a[-1][3],'%Y-%m-%dT%H:%M:%S'),a[-1][3])
				ct+=1
			days=('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')
			with open('tesfile.csv','w') as csvfile:
				w=csv.writer(csvfile)
				w.writerow(['Location','date','time','duration','intensity (85%ile delay)'])
				for dis in sorted(summ,reverse=True,key= lambda x:x[2]*x[3]):
					w.writerow([n,days[dis[0].weekday()]+','+str(dis[0].date()),str(str(dis[0].time())+'-'+str(dis[1])),dis[2],dis[3]])
			plt.title(n+"\nUpdated "+str(datetime.datetime.now()),fontsize=10)
			x1,x2,y1,y2 = plt.axis()
			plt.axis((5,24,y1,y2))
			plt.xlabel('Hour Starting',fontsize=8)
			plt.ylabel('Days',fontsize=8)
			plt.savefig(fileloc+n+'bus.png',dpi=150)
			plt.close()
			
			'''wks=8
			thing=lastxweeks(datetime.datetime.now(),wks)
			g2=[]
			for a in thing:
				l= ((datetime.datetime.now().date()-a[2]).days)
				if l>0:
					g2.append([a[1],cumulativedelayminutes(getdata(quick[n],day=l))])
				else:
					g2.append([a[1],0])
				print (g2[-1])
			col=[z for z in ['red','green','blue','purple','black','orange','grey']for zz in range(wks+1)]
			plt.bar(range(len(g2)),[b[1] for b in g2],color=col)
			start, end = plt.gca().get_xlim()
			plt.xticks(range(int(len(g2))),[a[0] for a in g2],rotation=90,fontsize=6)
			plt.title(n+" Bus Delays\nUpdated "+str(datetime.datetime.now()))
			plt.xlabel('Day')
			plt.ylabel('Delay minutes')
			plt.savefig(fileloc+n+"busdelay.png")
			plt.close()
			'''
			sys.exit(0)
			time.sleep(60)


# how many times 10% above threshold
# maximum delay
# incident lemgth - sustained over 10%
