import json
import mysql.connector
from datetime import datetime, timedelta,date  
from matplotlib import pyplot as plt
import numpy as np
import telegram
import os.path
import boto3
from io import StringIO, BytesIO

mydb = mysql.connector.connect(
  host="database-1.cyxb0drmxfft.us-east-1.rds.amazonaws.com",
  user="admin",
  password="admin123",

  database="CalDB"
)
s3 = boto3.client('s3')
bot = telegram.Bot('758389493:AAExlM5jAb1OvyG9ZBYXyPzbnaO2SslQUWo')
mycursor = mydb.cursor()

def daily_pie_chart(p_date):
  sql = "SELECT event_cal_name,event_color,sum(TIME_TO_SEC(event_diff_time)) FROM CalDB.cal_events_data where event_start_date = '" + str(p_date) +"' group by event_cal_name,event_color"
  mycursor.execute("SET SESSION time_zone = '+5:30';")
  mycursor.execute(sql)

  myresult = mycursor.fetchall()
  print(myresult)
  labels = []
  times = []
  colorset = []
  tt  = 0
  NR  = 0 
  NDR = 0
  NWC = 0
  NPW = 0
  NSC = 0
  NMU = 0
  for x in myresult:    
    print(x[0], ' ' ,x[1], ' ' , timedelta(seconds= int(x[2]) ) )
    labels.append(str(timedelta(seconds= int(x[2]))))
    colorset.append(str(x[1]))
    times.append(str(x[2]))
    tt = tt + int(x[2])
    if x[0] == 'Naveen Routine':
        NR  = float(int(x[2])/3600)
    elif x[0] == 'Naveen Daily Routine':
        NDR = float(int(x[2])/3600)
    elif x[0] == 'Naveen Work Calendar':
        NWC = float(int(x[2])/3600)
    elif x[0] == 'Naveen Personal Work':
        NPW = float(int(x[2])/3600)   
    elif x[0] == 'Naveen Sleep Calendar':
        NSC = float(int(x[2])/3600)
    elif x[0] == 'Naveen Mobile TV Usage':
        NMU = float(int(x[2])/3600)  
        
  plt.cla()
  plt.clf()
  
  img_data = BytesIO()
  totaltime = str(timedelta(seconds= tt))
  titles ="Displaying for " + totaltime + " hrs " + str(p_date) 
  plt.title(titles)
  plt.tight_layout()   
  plt.style.use("fivethirtyeight")
  plt.pie(times, labels = labels,colors = colorset ,autopct='%1.2f%%'
  , shadow= True , wedgeprops= {'edgecolor' : 'white' }
  )  
  #plt.pie(times, labels = labels,colors = colorset ,autopct='%1.2f%%') 
  #plt.savefig('activity.png') 
  plt.savefig(img_data, format='png')
  img_data.seek(0)
  # put plot in S3 bucket
  t_key = 'Daily_Activity.png'
  bucket = boto3.resource('s3').Bucket('mycalactivity')
  bucket.put_object(Body=img_data, ContentType='image/png', Key=t_key)
  #generate presigned url
  url = s3.generate_presigned_url('get_object', 
      Params={'Bucket': 'mycalactivity', 'Key': t_key},
      ExpiresIn=86400)
  print(url)
  #bot.send_photo(chat_id='582942300', photo=url)
  NSC_D = ''
  NWC_D = ''
  NPW_D = ''
  NDR_D = ''
  NMU_D = ''
  NR_D  = ''
  CON   = ''
  if NSC > 9.5:
    NSC_D = '<b>' + 'You are wasting time on Bed sleeping' + '</b>'
  elif NSC >= 8.5 and NSC <=9.5:
    NSC_D = '<i>' + 'You have slept enough time today' + '</i>'   
  else:
    NSC_D = '<b>' + '**You are not sleeping well**' + '</b>'
  
  if NWC >5:       
    NWC_D = '<b>' + 'You are working more than enough' + '</b>'
  elif NWC >= 4 and NSC <=5:       
    NWC_D = '<i>' + 'You have worked enough time today' + '</i>'          
  else:
    NWC_D = 'Spend some time on Office Work'
  
  if NPW > 3:       
    NPW_D = '<i>' + 'You Learnt more today :)' + '</i>' 
  elif NPW >= 1 and NPW <= 3:       
    NPW_D = '<i>' + 'You have spent enough time on Learning' + '</i>'        
  else:       
    NPW_D = '<b>' + '**Spend some time on Learning**' + '</b>'
  
  if NDR > 5.5:       
    NDR_D = '<b>' + 'You are wasting time on routine activities' + '</b>'
  elif NDR >= 4.5 and NDR <= 5.5:       
    NDR_D = '<i>' + 'You have spent enough time on routines' + '</i>'          
  else:
    NDR_D = '<b>' + '**Please take care of your health**'  + '</b>'
    
  if NMU > 2:       
    NMU_D = '<b>' + '*You are wasting time on Gadgets*' + '</b>'
  elif NMU > 1 and NMU <= 2:       
    NMU_D = 'You have spent enough time on Gadgets'   
  else:
    NMU_D = '<i>' + 'Good you havent wasted time on Gadgets' + '</i>'    
  
  if NR > 0:     
    NR_D = '<i>' + 'You have done something special today' + '</i>'        
  else:
    NR_D = 'Nothing new today'
    
  if NWC + NPW > 8:
    CON = '<b>' + '***Missing work life blance***'  + '</b>'
  
    
  caption = '<b>' + 'Your Day Activity' + '</b>\n' +  NWC_D + '\n' + NPW_D + '\n' + NSC_D + '\n' + NMU_D + '\n' + NDR_D + '\n' + NR_D + '\n' +  CON          
  #bot.send_message(chat_id='582942300',text= caption ,parse_mode = 'HTML')
  bot.send_photo(chat_id='582942300', photo= url, caption = caption,parse_mode = 'HTML')
  return response('<html><head><title>Daily Activity</title></head>' + 
        '<body><div><img src=' + url + ' alt="Image" width="750" height="600"><div><p>' + caption+ '</p></body></html>')

def response(myhtml):
    return {
        "statusCode": 200,
        "body": myhtml,
        "headers": {
            "Content-Type": "text/html",
        }
    }
  
def lambda_handler(event, context):
    # TODO implement
    try: 
        t_date = event.get('queryStringParameters')['date']
    except Exception as e:
        t_date = date.today()
        
    robj = daily_pie_chart(t_date)
    return robj

#lambda_handler(1, 1)