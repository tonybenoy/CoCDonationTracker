from cocapi import CocApi
from pprint import PrettyPrinter
import time
import jsondiff
import datetime
import pymongo
import redis
newdata = None
olddata =None
def getdata(token):
    api = CocApi(token)
    clan = api.clan_members("#PU8J2RQ")
    data = {
        "datetime" : datetime.datetime.utcnow()
    }
    membdata = []
    for item in clan["items"]:
        membdata.append({"name":item["name"]+item["tag"],
                        "donations":item["donations"],
                        "donationsReceived":item["donationsReceived"]})
    data["members"] = membdata
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydatabase"]
    collist = mydb.list_collection_names()
    if "donations" in collist:
        mycol = mydb["donations"]
    else:
        mycol = mydb.create_collection("donations",capped=True,size=2**20,max=200)
    x = mycol.insert_one(data)
    global olddata,newdata
    if newdata == None:
        olddata = x.inserted_id
    else:
        olddata = newdata
    newdata = x.inserted_id
    
  
def donations():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["mydatabase"]
    mycol = mydb["donations"]
    myquery1 = {"_id": newdata}
    a = mycol.find(myquery1)
    myquery2 = {"_id": olddata}
    b = mycol.find(myquery2)
    pp = PrettyPrinter()
    curr=None
    old=None
    for x,y in zip(a,b):
        print(jsondiff.diff(x["members"], y["members"]))
        if (jsondiff.diff(x["members"], y["members"])) != {}:
            pp.pprint(x)
            pp.pprint(y)
            for item in (jsondiff.diff(x["members"], y["members"])):
                if type(item)== int:
                    given_diff = x["members"][item]["donations"] - y["members"][item]["donations"]
                    rec_diff = x["members"][item]["donationsReceived"] - \
                        y["members"][item]["donationsReceived"]
                    name = x["members"][item]["name"]
                    print(name,given_diff,rec_diff)
if __name__ == "__main__":
    token = ""
    count = 0
    while(True):
        count+=1
        pp = PrettyPrinter()
        pp.pprint( getdata(token))
        time.sleep(3)
        print("-----------------------------------"+str(count))
        donations()
