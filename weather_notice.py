import requests as req
import json
import datetime as dt
import time
from math import log10
import geopy
import win11toast
from pystray import Icon,Menu,MenuItem
from PIL import Image
import threading
import sys
import re
import csv
import urllib.request
from bs4 import BeautifulSoup
from matplotlib import pyplot as pyp

data_old="\n"
req_num=0
sound_pro=True
earth_dic={}
earth_tmp={}
co=True

output_file = "..\\data\\earthquake.csv"
output_file_old = "..\\data\\earthquake_old.csv"
# output_file = "earthquake.csv"
# output_file_old = "earthquake_old.csv"

header = ["イベントID","地震発生場所","地震発生時刻","観測点で地震を検知した時刻","緯度","経度",
          "マグニチュード","県名称","市町村名称","最大震度","震度観測点の情報"]

WEATHER_TRANS = json.load(open("..\\data\\transweather.json", "r",encoding="utf-8"))
OFFICES_AREA_CODE = "230000"
CLASS_AREA_CODE = "2320300"
AREA_URL = "https://www.jma.go.jp/bosai/common/const/area.json"
warning_bool=False
warning_text_new=[]
warning_text_old=[]
warning_status=[]
warning_text=[]
req_num=0
BOUHU = False
base_1=dt.time(6, 35, 0)
base_2=dt.time(11, 0, 0)
time_fmt=""

def weather():
    def night():
        hourly_time=[]
        hourly_rain=[]
        weather_json=req.get("https://api.open-meteo.com/v1/forecast?latitude=35.30&longitude=136.80&timezone=Asia%2FTokyo&daily=temperature_2m_max&daily=temperature_2m_min&daily=precipitation_probability_mean&daily=weathercode&daily=windspeed_10m_max&daily=winddirection_10m_dominant&hourly=relativehumidity_2m&hourly=rain",verify=False)
        weather_json=weather_json.json()

        rain_mm=weather_json["hourly_units"]["rain"]
        temp_sym=weather_json["daily_units"]["temperature_2m_max"]
        rain_sym=weather_json["daily_units"]["precipitation_probability_mean"]
        wind_sym=weather_json["daily_units"]["windspeed_10m_max"]
        situdo=0
        for i in range(24,49):
            hourly_time.append(weather_json["hourly"]["time"][i])
            tmp=hourly_time[i-24]
            tmp=tmp.replace("2023-","")
            hourly_time[i-24]=tmp.replace("T"," ")
            hourly_rain.append(weather_json["hourly"]["rain"][i])
            situdo+=int(weather_json["hourly"]["relativehumidity_2m"][i])
        situdo=situdo//24
        fig=pyp.figure(figsize=[12,5])
        ax=fig.add_subplot(111)
        fig.tight_layout()
        ax.bar(hourly_time, hourly_rain,width=1,align="edge")
        ax.set_xlabel("Data")
        ax.set_ylabel("mm/h")
        pyp.xticks(rotation=15)
        fig.savefig("..\\data\\graph.png")
        pyp.cla()

        day=weather_json["daily"]["time"][1]
        temp_max=weather_json["daily"]["temperature_2m_max"][1]
        temp_min=weather_json["daily"]["temperature_2m_min"][1]
        humi_mean=weather_json["daily"]["precipitation_probability_mean"][1]
        weather_code=weather_json["daily"]["weathercode"][1]
        wind_max=weather_json["daily"]["windspeed_10m_max"][1]
        wind_di=weather_json["daily"]["winddirection_10m_dominant"][1]
        wind_str="None"
        weather_str="None"
        if wind_di >=0 and wind_di <22.4:
            wind_str="北"
        elif wind_di >= 22.5 and wind_di < 44.9:
            wind_str="北北東"
        elif wind_di >= 22.5 and wind_di < 44.9:
            wind_str="北東"
        elif wind_di >= 45 and wind_di < 67.4:
            wind_str="東北東"
        elif wind_di >= 67.5 and wind_di < 89.9:
            wind_str="東"
        elif wind_di >= 90 and wind_di < 112.4:
            wind_str="東南東"
        elif wind_di >= 112.5 and wind_di < 134.9:
            wind_str="南東"
        elif wind_di >= 135 and wind_di < 157.4:
            wind_str="南南東"
        elif wind_di >= 157.5 and wind_di < 179.9:
            wind_str="南"
        elif wind_di >= 180 and wind_di < 202.4:
            wind_str="南南西"
        elif wind_di >= 202.5 and wind_di < 224.9:
            wind_str="南西"
        elif wind_di >= 225 and wind_di < 247.4:
            wind_str="西北西"
        elif wind_di >= 247.5 and wind_di < 269.9:
            wind_str="西"
        elif wind_di >= 270 and wind_di < 292.4:
            wind_str="西北西"
        elif wind_di >= 292.5 and wind_di < 314.9:
            wind_str="北西"
        elif wind_di >= 315 and wind_di < 337.4:
            wind_str="北北西"
        elif wind_di >= 337.5 and wind_di <= 360:
            wind_str="北"

        if weather_code == 0 :
            weather_str = "快晴"
        elif weather_code >= 1 and weather_code <=3:
            weather_str = "晴れ時々曇り、曇り"
        elif weather_code == 45 or weather_code == 48:
            weather_str = "小雨"
        elif weather_code == 51 or weather_code == 53 or weather_code == 55:
            weather_str = "霧雨"
        elif weather_code >= 56 and weather_code <=57:
            weather_str = "氷結霧雨"
        elif weather_code == 61 or weather_code == 63 or weather_code == 65:
            weather_str = "雨"
        elif weather_code >= 66 and weather_code <=67:
            weather_str = "冷たい雨"
        elif weather_code == 71 or weather_code == 73 or weather_code == 75:
            weather_str = "雪"
        elif weather_code >= 77:
            weather_str = "にわか雪"
        elif weather_code >= 80 and weather_code <=82:
            weather_str = "にわか雨"
        elif weather_code >= 85 and weather_code <=86:
            weather_str = "雪"
        elif weather_code == 95:
            weather_str = "強雨"
        elif weather_code == 96 or weather_code == 99:
            weather_str = "雷雨"

        wind_max=(wind_max/3600)*1000

        send_contents=f"{day}の天気\n最高気温:{temp_max}{temp_sym} 最低気温:{temp_min}{temp_sym} \n湿度:{situdo}%\n天気:{weather_str} {humi_mean}{rain_sym}\n最大風速:{int(wind_max)}m/s 風向:{wind_str}"
        try:
            win11toast.toast("天気",send_contents,image="file:///..\\data\\graph.png",duration="short")
        except Exception as e:
            pass

    def day():
        hourly_time=[]
        hourly_rain=[]
        weather_json=req.get("https://api.open-meteo.com/v1/forecast?latitude=35.30&longitude=136.8125&timezone=Asia%2FTokyo&daily=temperature_2m_max&daily=temperature_2m_min&daily=precipitation_probability_mean&daily=weathercode&daily=windspeed_10m_max&daily=winddirection_10m_dominant&hourly=rain",verify=False)
        weather_json=weather_json.json()

        rain_mm=weather_json["hourly_units"]["rain"]
        temp_sym=weather_json["daily_units"]["temperature_2m_max"]
        rain_sym=weather_json["daily_units"]["precipitation_probability_mean"]
        wind_sym=weather_json["daily_units"]["windspeed_10m_max"]
        for i in range(0,24):
            hourly_time.append(weather_json["hourly"]["time"][i])
            tmp=hourly_time[i]
            tmp=tmp.replace("2023-","")
            hourly_time[i]=tmp.replace("T"," ")
            hourly_rain.append(weather_json["hourly"]["rain"][i])
        fig=pyp.figure(figsize=[12,5])
        ax=fig.add_subplot(111)
        fig.tight_layout()
        ax.bar(hourly_time, hourly_rain,width=1,align="edge")
        ax.set_xlabel("Data")
        ax.set_ylabel("mm/h")
        pyp.xticks(rotation=15)
        fig.savefig("..\\data\\graph.png")
        pyp.cla()

        day=weather_json["daily"]["time"][0]
        temp_max=weather_json["daily"]["temperature_2m_max"][0]
        temp_min=weather_json["daily"]["temperature_2m_min"][0]
        humi_mean=weather_json["daily"]["precipitation_probability_mean"][0]
        weather_code=weather_json["daily"]["weathercode"][0]
        wind_max=weather_json["daily"]["windspeed_10m_max"][0]
        wind_di=weather_json["daily"]["winddirection_10m_dominant"][0]
        wind_str="None"
        weather_str="None"
        if wind_di >=0 and wind_di <22.4:
            wind_str="北"
        elif wind_di >= 22.5 and wind_di < 44.9:
            wind_str="北北東"
        elif wind_di >= 22.5 and wind_di < 44.9:
            wind_str="北東"
        elif wind_di >= 45 and wind_di < 67.4:
            wind_str="東北東"
        elif wind_di >= 67.5 and wind_di < 89.9:
            wind_str="東"
        elif wind_di >= 90 and wind_di < 112.4:
            wind_str="東南東"
        elif wind_di >= 112.5 and wind_di < 134.9:
            wind_str="南東"
        elif wind_di >= 135 and wind_di < 157.4:
            wind_str="南南東"
        elif wind_di >= 157.5 and wind_di < 179.9:
            wind_str="南"
        elif wind_di >= 180 and wind_di < 202.4:
            wind_str="南南西"
        elif wind_di >= 202.5 and wind_di < 224.9:
            wind_str="南西"
        elif wind_di >= 225 and wind_di < 247.4:
            wind_str="西北西"
        elif wind_di >= 247.5 and wind_di < 269.9:
            wind_str="西"
        elif wind_di >= 270 and wind_di < 292.4:
            wind_str="西北西"
        elif wind_di >= 292.5 and wind_di < 314.9:
            wind_str="北西"
        elif wind_di >= 315 and wind_di < 337.4:
            wind_str="北北西"
        elif wind_di >= 337.5 and wind_di <= 360:
            wind_str="北"

        if weather_code == 0 :
            weather_str = "快晴"
        elif weather_code >= 1 and weather_code <=3:
            weather_str = "晴れ時々曇り、曇り"
        elif weather_code == 45 or weather_code == 48:
            weather_str = "小雨"
        elif weather_code == 51 or weather_code == 53 or weather_code == 55:
            weather_str = "霧雨"
        elif weather_code >= 56 and weather_code <=57:
            weather_str = "氷結霧雨"
        elif weather_code == 61 or weather_code == 63 or weather_code == 65:
            weather_str = "雨"
        elif weather_code >= 66 and weather_code <=67:
            weather_str = "冷たい雨"
        elif weather_code == 71 or weather_code == 73 or weather_code == 75:
            weather_str = "雪"
        elif weather_code >= 77:
            weather_str = "にわか雪"
        elif weather_code >= 80 and weather_code <=82:
            weather_str = "にわか雨"
        elif weather_code >= 85 and weather_code <=86:
            weather_str = "雪"
        elif weather_code == 95:
            weather_str = "強雨"
        elif weather_code == 96 or weather_code == 99:
            weather_str = "雷雨"

        wind_max=(wind_max/3600)*1000

        if int(temp_max)>=35:
            send_contents=f"今日の天気\n**WARNING**\n最高気温:{temp_max}{temp_sym} 最低気温:{temp_min}{temp_sym} \n天気:{weather_str} {humi_mean}{rain_sym}\n最大風速:{int(wind_max)}m/s 風向:{wind_str}"
        elif int(temp_max)>=30:
            send_contents=f"今日の天気\n**CAUTION**\n最高気温:{temp_max}{temp_sym} 最低気温:{temp_min}{temp_sym} \n天気:{weather_str} {humi_mean}{rain_sym}\n最大風速:{int(wind_max)}m/s 風向:{wind_str}"
        else:
            send_contents=f"今日の天気\n最高気温:{temp_max}{temp_sym} 最低気温:{temp_min}{temp_sym} \n天気:{weather_str} {humi_mean}{rain_sym}\n最大風速:{int(wind_max)}m/s 風向:{wind_str}"
        try:
            win11toast.toast("天気",send_contents,image="file:///..\\data\\graph.png",duration="short")
        except Exception as e:
            pass
    while True:
        if int(dt.datetime.now().hour) == 7 and int(dt.datetime.now().minute) == 0:
            day()
        elif int(dt.datetime.now().hour) == 19 and int(dt.datetime.now().minute) ==0:
            night()
        time.sleep(60)


def warning():
    url = "https://www.jma.go.jp/bosai/warning/data/warning/%s.json" % (OFFICES_AREA_CODE)
    def war_main():
        def warnings():
            global warning_text,warning_status,warning_texts,time_fmt
            try:
                area_data = urllib.request.urlopen(url=AREA_URL)
                area_data = json.loads(area_data.read())
                area = area_data["class20s"][CLASS_AREA_CODE]["name"]
                warning_info = urllib.request.urlopen(url=url)
                warning_info = json.loads(warning_info.read())
                time_fmt=warning_info["reportDatetime"]
                warning_codes = [warning["code"]
                                for class_area in warning_info["areaTypes"][1]["areas"]
                                    if class_area["code"] == CLASS_AREA_CODE
                                        for warning in class_area["warnings"]
                                            if warning["status"] != "発表警報・注意報はなし"]
                warning_status = [warning["status"]
                                for class_area in warning_info["areaTypes"][1]["areas"]
                                    if class_area["code"] == CLASS_AREA_CODE
                                        for warning in class_area["warnings"]]
                warning_texts = [WEATHER_TRANS["warninginfo"][code] for code in warning_codes]
                return (warning_texts,area)
            except Exception as e:
                print(f"Error {e}")
                pass
        def Bohu(send):
            pass
        global warning_bool,warning_text_new,warning_text_old,warning_status,warning_text,req_num,time_fmt,BOUHU
        try:
            print("https://www.jma.go.jp/bosai/warning/#area_type=class20s&area_code=%s&lang=ja" % (CLASS_AREA_CODE))
            print("%sの気象警報・注意報" % (warnings()[1]))
            if warnings()[0] == []:
                warning_bool=False
                print("現在発表警報・注意報はありません")
            else:
                warning_bool=True
            if warning_bool==True:
                warning_text_old=warning_text_new
                warning_text_new=warnings()[0]
                if warning_text_new!=warning_text_old:
                    if warning_status[0]!="発表警報・注意報はなし":
                        for i in range(len(warning_texts)):
                            warning_text.append(f"{warning_texts[i]}:{warning_status[i]}")
                    send=""
                    for i in range((len(warning_text))):
                        send=f"{send}{warning_text[i]}\n"
                    with open("..\\data\\warning_now.txt","w") as f:
                        f.write(send)
                        f.close()
                    with open("..\\data\\warning.txt", "r") as f:
                        txt_1=f.read()
                        f.close()
                    with open("..\\data\\warning_now.txt", "r") as f:
                        txt_2=f.read()
                        f.close()
                    if txt_1!=txt_2:
                        with open("..\\data\\warning.txt","w") as f:
                            f.write(str(txt_2))
                            f.close()
                        time_fmt_ = dt.datetime.strptime(time_fmt,"%Y-%m-%dT%H:%M:%S+09:00").strftime("%Y-%m-%d %H:%M:%S")
                        if "警報" in send:
                            if "暴風警報" in send:
                                send_contents2 = Bohu(send)
                                if send_contents2 == "":
                                    BOUHU = False
                                send_contents=f"\n***暴風警報***\n警報・注意報の情報\n{time_fmt_}発表\n{send}"
                            else:
                                send_contents=f"\n***警報***\n警報・注意報の情報\n{time_fmt_}発表\n{send}"
                        else:
                            send_contents=f"\n警報・注意報の情報\n{time_fmt_}発表\n{send}"
                        try:
                            win11toast.toast("警報・注意報",send_contents,duration="short")
                            with open("..\\data\\warning_log.txt","a",encoding="utf-8") as f:
                                f.write("================================================================")
                                f.write(f"{send_contents}\n")
                            print(send_contents)
                            if BOUHU ==True:
                                win11toast.toast("警報・注意報",send_contents2,duration="short")
                                with open("..\\data\\warning_log.txt","a",encoding="utf-8") as f:
                                    f.write(f"{send_contents2}\n")
                                print(send_contents2)
                                BOUHU = False
                            with open("..\\data\\warning_log.txt","a",encoding="utf-8") as f:
                                f.write("================================================================\n")
                        except Exception as e:
                            pass
            warning_text=[]
        except Exception as e:
            pass
    while True:
        war_main()
        time.sleep(60)


def quake():
    while True:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                writer = csv.writer(f, lineterminator="\n")
                writer.writerow(header)

                url = "http://www.data.jma.go.jp/developer/xml/feed/eqvol.xml"
                res = urllib.request.urlopen(url).read()
                soup = BeautifulSoup(res,features="html.parser")

                search = re.compile('.*VXSE.*')

                count = 0

                for vxse in soup.find_all(text=search):
                    if count == 0:

                        res = urllib.request.urlopen(vxse).read()
                        soup = BeautifulSoup(res,features="html.parser")

                        event_id = soup.find("eventid").text

                        headline = soup.find("headline").text

                        for content in soup.find_all("body"):
                            earthquake = content.find("earthquake")

                            if earthquake is not None:
                                location = earthquake.find("name").text
                                origintime = earthquake.find("origintime").text
                                arrivaltime = earthquake.find("arrivaltime").text

                                coordinate = earthquake.find("jmx_eb:coordinate").text
                                lat = coordinate[1:coordinate[1:].find("+") + 1]
                                lon = coordinate[coordinate[1:].find("+") + 2:coordinate[1:].find("+") + 7]
                                try:
                                    lat = int(lat[0:2])+(int(lat[3:])/60)+(0/3600)
                                    lon = int(lon[0:3])+(int(lon[4:])/60)+(0/3600)
                                except Exception as e:
                                    lat="null"
                                    lon="null"
                                magnitude = earthquake.find("jmx_eb:magnitude").text

                            intensity = content.find("intensity")
                            if intensity is not None:
                                for pref in intensity.find_all("pref"):

                                    try:
                                        prefectuer = pref("name")[0].text
                                    except Exception as e:
                                        prefectuer="null"

                                    for city in pref.find_all("city"):
                                        city_name = city("name")[0].text
                                        maxint = city("maxint")[0].text

                                        write_list = []
                                        write_list.append(event_id)
                                        write_list.append(location)
                                        write_list.append(origintime)
                                        write_list.append(arrivaltime)
                                        write_list.append(lat)
                                        write_list.append(lon)
                                        write_list.append(magnitude)
                                        try:
                                            write_list.append(prefectuer)
                                        except Exception as e:
                                            pass
                                        write_list.append(city_name)
                                        write_list.append(maxint)

                                        intensity_station = ""
                                        for intensitystation in pref.find_all("intensitystation"):
                                            intensity_station = intensity_station + intensitystation("name")[0].text + " "

                                        write_list.append(intensity_station)

                                        writer.writerow(write_list)
                        count+=1
                    else:
                        break
                f.close()
            with open(output_file, 'r',encoding="utf-8_sig") as f:
                file_read1=f.read()
                f.close()
            with open(output_file_old, 'r',encoding="utf-8_sig") as f:
                file_read2=f.read()
                f.close()

            if file_read1 != file_read2:
                mag=float(magnitude)
                if mag >=5:
                    urls=f'https://typhoon.yahoo.co.jp/weather/jp/earthquake/{event_id}.html'
                    try:
                        send_contents=f"""{headline}\n地震発生場所:{location}\n発生時刻:{origintime}\n北緯:{lat}\n東経:{lon}
                                            \nマグニチュード:{magnitude}\n県名称:{prefectuer} 市町村名称:{city_name} 最大震度:{maxint}\n URL:{urls}"""
                    except Exception as e:
                        send_contents=f"""{headline}\n地震発生場所:{location}\n発生時刻:{origintime}\n北緯:{lat}\n東経:{lon}
                                            \nマグニチュード:{magnitude}\n URL:{urls}"""
                    send_dic = {'message': send_contents}
                    try:
                        win11toast.toast("地震速報",send_contents,duration="short")
                    except Exception as e:
                        pass
                    with open(output_file_old,'w',encoding="utf-8_sig") as f:
                        f.write(file_read1)
                        f.close()
                else:
                    with open(output_file_old,'w',encoding="utf-8_sig") as f:
                        f.write(file_read1)
                        f.close()
            else:
                pass
        except Exception as e:
            pass
        time.sleep(60)
        if co==False:
            break

def tasktray_create():
    try:
        global icon
        item=[]
        options_map={'設定':Menu(MenuItem('音声',Menu(MenuItem('音声ON',lambda:tasktray_sound_on(),default=False),
                                                    MenuItem('音声OFF',lambda:tasktray_sound_off(),default=False)),default=False)),
                    '現在状況':lambda:tasktray_now(),"終了":lambda:tasktray_abort()}

        for option,callback in options_map.items():
            item.append(MenuItem(option,callback,default=True if option=='Show' else False))
        menu=Menu(*item)
        image=Image.open("..\\earth_qu.ico")
        #image=Image.open("C:\\Users\\REI\\Downloads\\earth_qu.ico")
        icon=Icon("name",image,"My System Tray Icon",menu)
        icon.run()
    finally:
        tasktray_abort()

def tasktray_sound_on():
    global sound_pro
    sound_pro=True
    win11toast.toast("音声","ON",duration="short")

def tasktray_sound_off():
    global sound_pro
    sound_pro=False
    win11toast.toast("音声","OFF",duration="short")

def tasktray_now():
    global req_num
    win11toast.toast("現在状況",f"{req_num} requests",duration="short")

def tasktray_abort():
    global icon,co
    if icon != 0:
        co=False
        icon.stop()
    co=False

def main():
    global data_old,earth_dic,earth_tmp,sound_pro
    def get(time_now):
        try:
            json_data=req.get(f"http://www.kmoni.bosai.go.jp/webservice/hypo/eew/{time_now}.json").json()
            return json_data
        except Exception as e:
            win11toast.toast("ネットワーク警告",f"インターネットに接続されていない可能性があります。\nError:{e}",duration="short")
    def sum_sindo(latitude,longitude,depth,magJMA):
        Predicted_latitude = xxx
        Predicted_longitude = xxx
        epicenterLocaltion = [latitude, longitude]
        pointLocaltion = [Predicted_latitude, Predicted_longitude]
        magW = magJMA-0.171
        long = 10**(0.5*magW-1.85)/2
        epicenterDistance = geopy.distance.geodesic(epicenterLocaltion, pointLocaltion).km
        hypocenterDistance = (depth**2+epicenterDistance**2)**0.5-long
        x = max(hypocenterDistance, 3)
        gpv600 = 10**(0.58*magW+0.0038*depth-1.29 -
        log10(x+0.0028*(10**(0.5*magW)))-0.002*x)
        arv = 1.0
        pgv400 = gpv600*1.31
        pgv = pgv400*arv
        intensity = 2.68+1.72*log10(pgv)
        if intensity < 0.5:
            earthquake_intensity = "震度0"
        elif intensity >= 0.5 and intensity < 1.5:
            earthquake_intensity = "震度1"
        elif intensity >= 1.5 and intensity < 2.5:
            earthquake_intensity = "震度2"
        elif intensity >= 2.5 and intensity < 3.5:
            earthquake_intensity = "震度3"
        elif intensity >= 3.5 and intensity < 4.5:
            earthquake_intensity = "震度4"
        elif intensity >= 4.5 and intensity < 5.0:
            earthquake_intensity = "震度5弱"
        elif intensity >= 5.0 and intensity < 5.5:
            earthquake_intensity = "震度5強"
        elif intensity >= 5.5 and intensity < 6.0:
            earthquake_intensity = "震度6弱"
        elif intensity >= 6.0 and intensity < 6.5:
            earthquake_intensity = "震度6強"
        elif intensity >= 6.5:
            earthquake_intensity = "震度7"
        return earthquake_intensity

    try:
        send_data=""
        now=dt.datetime.now()
        now=now-dt.timedelta(seconds=2)
        now=now.strftime("%Y%m%d%H%M%S")
        json_data=get(now)
        if json_data["result"]["message"]!="データがありません":
            if json_data["is_training"]==False:
                if float(json_data["magunitude"]) >=5:
                    print(earth_dic)
                    if json_data['report_id'] not in earth_dic:
                        earth_tmp={json_data['report_id']:[]}
                        earth_dic.update(earth_tmp)
                    if json_data['report_id'] in earth_dic:
                        tmp_Tr=False
                        for i in earth_dic.keys():
                            if i==json_data['report_id']:
                                for x in range(len(earth_dic[i])):
                                    if earth_dic[i][x]==json_data['report_num']:
                                        tmp_Tr=True
                                    if tmp_Tr==True:
                                        break
                        if tmp_Tr==False:
                            earth_dic[json_data['report_id']].append(json_data['report_num'])
                            if json_data["is_cancel"]!=True:
                                send_data=f"{send_data}ID:{json_data['report_id']}\n第{json_data['report_num']}報 "
                                send_data=f"{send_data} 震源地:{json_data['region_name']}\n深さ:{json_data['depth']} "
                                send_data=f"{send_data} 最大震度:{json_data['calcintensity']} マグニチュード:{json_data['magunitude']}/n"
                                depth_fo=json_data['depth']
                                depth_fo=depth_fo.replace("km","")
                                send_data=f"{send_data} 一宮市の予測震度:{sum_sindo(float(json_data['latitude']),float(json_data['longitude']),float(depth_fo),float(json_data['magunitude']))}"
                            elif json_data["is_cancel"]==True:
                                send_data="***緊急地震速報はキャンセルされました。***"
                            print(send_data)
                            if send_data!=data_old:
                                with open("..\\data\\earth_now_log.txt","a",encoding="utf-8") as f:
                                    f.write("================================================================")
                                    f.write(f"\n{now}")
                                    f.write(f"{send_data}\n")
                                    f.write("================================================================\n")
                                if sound_pro:
                                    win11toast.toast("地震速報",send_data,audio="https://soundsard.com/wp-content/uploads/2022/09/dongdat-alert.mp3",duration="short")
                                else:
                                    win11toast.toast("地震速報",send_data,duration="short")
        data_old=send_data
    except Exception as e:
        pass

if __name__ == "__main__":
    warning_we=threading.Thread(target=warning)
    warning_we.setDaemon(True)
    weather_=threading.Thread(target=weather)
    weather_.setDaemon(True)
    create=threading.Thread(target=tasktray_create)
    create.setDaemon(True)
    quake_=threading.Thread(target=quake)
    quake_.setDaemon(True)
    main_=threading.Thread(target=main)
    main_.setDaemon(True)
    weather_.start()
    warning_we.start()
    create.start()
    quake_.start()
    while True:
        try:
            req_num+=1
            main_.start()
            time.sleep(1)
        except Exception as e:
            time.sleep(1)
        if co==False:
            sys.exit()
