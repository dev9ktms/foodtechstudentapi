from fastapi import FastAPI, HTTPException,Depends
from pydantic import BaseModel, Field
import models,schemas
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
import requests
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.config import Config


# from google.oauth2 import id_token
# from google.auth.transport import requests
from databases import Database
import psycopg2

con= psycopg2.connect(host='ktms-database.cms5s3jnyltw.ap-south-1.rds.amazonaws.com',user='postgres',password='postgres',database='ktms')
con.autocommit=True
cur=con.cursor()


database=Database("postgres://postgres:postgres@ktms-database.cms5s3jnyltw.ap-south-1.rds.amazonaws.com:5432/ktms")

app = FastAPI()

@app.on_event("startup")
async def database_start():
    await database.connect()

@app.on_event("shutdown")
async def database_shutdown():
    await database.disconnect()

origins = ["http://localhost:3000",]
app.add_middleware(SessionMiddleware,secret_key="idontknow", session_cookie='cookie22')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db= SessionLocal()
        yield db
    finally:
        db.close()

config = Config(".env")
oauth = OAuth(config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@app.get('/student/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    print(redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/student/auth")
async def auth(request: Request, db: Session=Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)

        user=db.query(models.Students).filter(models.Students.email==token.get('userinfo')['email']).first()
        if user is None:
            userinfo = token.get('userinfo')
            newUser = models.Students()
            newUser.name = userinfo['name']
            newUser.email = userinfo['email']
            db.add(newUser)
            db.commit()
            print(newUser)
        loginSession = models.SessionModel()
        loginSession.sessionId = token.get('access_token')
        loginSession.email = token.get('userinfo')['email']
        db.add(loginSession)
        db.commit()
       response = RedirectResponse(
            url="http://localhost:3000/authredirect/student?token="+str(token.get('access_token')))
        return response
    except ValueError:
        raise HTTPException(status_code=498, detail=ValueError)

@app.get('/student/getuser')
async def auth(request: Request, db: Session=Depends(get_db)):
    token = request.headers["Authorization"]
    userResponse = db.query(models.SessionModel).filter(models.SessionModel.sessionId==token).first()
    print(userResponse.email)
    email = userResponse.email
    if email:
        userInfo =db.query(models.Students).filter(models.Students.email==email).first()
        response = {
            "user": {
                'name':userInfo.name,
                'email':userInfo.email,
                'institute':userInfo.institute
            }
        }
        print(response)
        return JSONResponse(status_code=200, content=response) 
    else:
        raise HTTPException(status_code=498, detail={'msg': 'Invalid Token'})

@app.get("/student/get-user-list")
def  read_api(db: Session=Depends(get_db)):
    return db.query(models.Students).all()

@app.get("/student/get-consumption-history")
def get_consumption_history(db: Session=Depends(get_db)):
    return db.query(models.Consumption).all()

@app.post("/student/create-user")
def create_user(user: schemas.Student, db: Session=Depends(get_db)):
    
    user_model=db.query(models.Students).filter(models.Students.email==user.email).first()
    user_model.Age = user.Age
    user_model.Gender= user.Gender
    user_model.Address_line_1=user.Address_line_1
    user_model.Address_line_2=user.Address_line_2
    user_model.City=user.City
    user_model.State=user.State
    user_model.Pincode=user.Pincode
    user_model.Country=user.Country
    user_model.Phone=user.Phone
    user_model.institute=user.institute



    db.add(user_model)
    db.commit()

    return user

@app.post("/student/post-student-order")
def create_user(user: schemas.StudentOrderSchema, db: Session=Depends(get_db)):
    
    user_model=db.query(models.Students).filter(models.Students.email==user.user_id).first()
    order_data=models.StudentOrder()
    order_data.Address_line_1=user_model.Address_line_1
    order_data.Address_line_2=user_model.Address_line_2
    order_data.Phone=user_model.Phone
    order_data.institute=user_model.institute
    order_data.name=user_model.name
    order_data.email=user_model.email
    order_data.date=user.date
    order_data.outlet_name=user.outlet_name

    food=''
    Foodprice=''
    quantity=''

    for i in range(len(user.items)) :
        food+=user.items[i]+'_'
        Foodprice+=str(user.prices[i])+'_'
        quantity+=str(user.quantities[i])+'_'
            
    order_data.items=food
    order_data.prices=Foodprice
    order_data.quantities=quantity
    db.add(order_data)
    db.commit()

    return user

@app.post("/student/add-consumption-history")
def add_consumption_history(foodconsumption:schemas.FoodConsumption, db: Session=Depends(get_db)):

    consumption_model = models.Consumption()
    consumption_model.student_phone=foodconsumption.student_phone
    consumption_model.date=foodconsumption.date
    consumption_model.type=foodconsumption.type
    consumption_model.total_calories=foodconsumption.total_calories
    # consumption_model.institute=foodconsumption.institute

    data=db.query('')

    db.add(consumption_model)
    db.commit()

    return foodconsumption



@app.put("/student/update-user/{user_id}")
def update_user(user_id:int, user:schemas.Student,db:Session=Depends(get_db)):
    user_model=db.query(models.Students).filter(models.Students.email==user_id).first()

    if user_model is None:
        raise  HTTPException(
            status_code=404,
            detail=f"ID {user_id} : Does Not Exist"
        )


    # user_model.password = user.password
    user_model.Age = user.Age
    user_model.Gender= user.Gender
    user_model.Address_line_1=user.Address_line_1
    user_model.Address_line_2=user.Address_line_2
    user_model.City=user.City
    user_model.State=user.State
    user_model.Pincode=user.Pincode
    user_model.Country=user.Country
    user_model.Phone=user.Phone
    user_model.email=user.email
    user_model.institute=user.institute
  

    db.add(user_model)
    db.commit()

    return user

@app.get("/student/isNewUser/{email_id}")
async def isNewUser(email_id,db:Session=Depends(get_db)):

    user_model=db.query(models.Students).filter(models.Students.email==email_id).first()

    if user_model.Phone is None:
        return True
    return False

@app.get("/student/get-mess_menu/{date}/{institute}")
async def get_mess_menu(date:str,institute:str):

    query1="SELECT * FROM vendor WHERE isapproved={}".format('true')

    isApproved = await  database.fetch_all(query=query1)
    insti="'{}'".format(institute)
    # print(isApproved[0].email=="dev1@ktms.in")
    menuList = []
    date="'{}'".format(date)
    if(isApproved):
      for i in range(len(isApproved)):
        if isApproved[i].isapproved == True:
          email="'{}'".format(isApproved[i].email)
          query2="SELECT * FROM menu WHERE institute="+str(insti)+" AND date={}".format(date)+" AND user_id="+str('{}'.format(str(email)))
          print(query2)
          menu=cur.execute(query2).fetchall()
        #   print(menu[0][12])
          
          if menu:
            data={}
            data["mess_name"]=menu[0][12]
            data["breakfast"]=menu[0][2]
            data["lunch"]=menu[0][3]
            data["snacks"]=menu[0][4]
            data["dinner"]=menu[0][5]
            menuList.append(data)
          
    print(menuList)
    # return JSONResponse(status_code=200, content={'msg':'menu send sucessfully'})






    # mess_menu=requests.get("http://localhost:8001/menu/get-menu-for-day/"+date+"/"+institute)
    # output=mess_menu.json()
    # print(output)
    return menuList

@app.get("/student/get-internalvendor-mess_menu/{institute}")
async def get_internal_mess_menu(institute:str,db:Session=Depends(get_db)):

    query1="SELECT * FROM vendor WHERE isapproved=true AND status=true"

    isApproved = await  database.fetch_all(query=query1)
    # isApproved= cur.execute(query1).fetchall()
    insti="'{}'".format(institute)
    print(isApproved[0].email=="dev1@ktms.in")
    menuList = []
    if(isApproved):
      for i in range(len(isApproved)):
        if isApproved[i].isapproved == True:
          email="'{}'".format(isApproved[i].email)
          query2="SELECT * FROM internalvendormenu WHERE institute="+str(insti)+" AND user_id="+str('{}'.format(str(email)))
          print(query2)
        #   menu=cur.execute(query2).fetchall()
        #   print(menu[0][12])
          menu = await  database.fetch_all(query=query2)
          
          if menu:
            data={}
            data["mess_name"]=menu[0][5]
            data["items"]=menu[0][2]
            data["prices"]=menu[0][3]
            items=menu[0][2].split("_")[:-1]
            data["ratings"]=""
            data["counts"]=""
            for j in range(len(items)):
             rating=db.query(models.StudentRating).filter(models.StudentRating.outlet_name==isApproved[i].mess_name,models.StudentRating.item==items[j]).all()
             if rating:
                 sum=0
                 count=len(rating)
                 for k in range(len(rating)):
                     sum+=rating[k].rating
                 data["ratings"]+=str(sum/count)+"_"
                 data["counts"]+=str(count)+"_"
             else:
                 data["ratings"]+="0_"
                 data["counts"]+="0_"
            data["status"]=isApproved[i].status
            # data["snacks"]=menu[0][4]
            # data["dinner"]=menu[0][5]
            menuList.append(data)
          
    print(menuList)
    return menuList

@app.get("/student/logout/{email_id}")
async def logout(email_id,db:Session=Depends(get_db)): 
    db.query(models.SessionModel).filter(models.SessionModel.email==email_id).delete()

    db.commit()

    return "user logged out successfully"

@app.post("/student/add-consumption-data")
async def add_consumption_data(data:schemas.ConsumptionHistorySchema,db:Session=Depends(get_db)):
    ispresent=db.query(models.ConsumptionHistory).filter(models.ConsumptionHistory.user_id==data.user_id,models.ConsumptionHistory.date==data.date,models.ConsumptionHistory.mess_name==data.mess_name,models.ConsumptionHistory.institute==data.institute).first()
    
    if ispresent:
        type=''
        for item in data.consumed:
          type+=item+'_'
        ispresent.consumed+=type
    
    else :
        new_consumption_history=models.ConsumptionHistory()
        new_consumption_history.user_id=data.user_id
        new_consumption_history.date=data.date
        new_consumption_history.mess_name=data.mess_name
        new_consumption_history.institute=data.institute
        type=''
        for item in data.consumed:
          type+=item+'_'
        new_consumption_history.consumed=type

        db.add(new_consumption_history)

    db.commit()

    data_=db.query(models.ConsumptionHistory).filter(models.ConsumptionHistory.user_id==data.user_id,models.ConsumptionHistory.date==data.date,models.ConsumptionHistory.mess_name==data.mess_name,models.ConsumptionHistory.institute==data.institute).first()
    
    calories_data=requests.get(f"http://localhost:8001/menu/get-calorie-data/{data_.mess_name}/{data_.date}/{data_.institute}/{data_.consumed}")
    output=calories_data.json()

    data_.calories_breakfast=output['calories_breakfast']
    data_.calories_lunch=output["calories_lunch"]
    data_.calories_dinner=output["calories_dinner"]
    data_.calories_snacks=output["calories_snacks"]
   
    db.commit()
    return "Consumption History Added successfully"

@app.get("/student/get-calories-history/{email}/{date}/{institute}")
async def get_calories_history(email:str, date:str, institute:str,db:Session=Depends(get_db)):
    data=db.query(models.ConsumptionHistory).filter(models.ConsumptionHistory.user_id==email,models.ConsumptionHistory.date==date,models.ConsumptionHistory.institute==institute).all()
    total_cal={}
    total_cal["breakfast"]=0
    total_cal["lunch"]=0
    total_cal["snacks"]=0
    total_cal["dinner"]=0
    print(data)

    for item in data:
        if item.calories_breakfast:
            total_cal["breakfast"]+=item.calories_breakfast
        if item.calories_lunch:
            total_cal["lunch"]+=item.calories_lunch
        if item.calories_snacks is not None:
            total_cal["snacks"]+=item.calories_snacks
        if item.calories_dinner:
            total_cal["dinner"]+=item.calories_dinner

    return total_cal

@app.get("/student/get-orders-history/{email}/{date}")
async def get_calories_history(email:str, date:str,db:Session=Depends(get_db)):
    email="'{}'".format(email)
    date="'{}'".format(date)
    query1="SELECT * FROM delivered_orders WHERE email_of_consumer="+email+" AND date="+date
    deliveredOrders= await  database.fetch_all(query=query1)
    data=[]
    for i in range(len(deliveredOrders)):
        menu={}
        menu["outlet_name"]=deliveredOrders[i][12]
        menu["items"]=deliveredOrders[i][9]
        menu["quantities"]=deliveredOrders[i][10]
        price=list(map(int,deliveredOrders[i][11].split("_")[:-1]))
        menu["total"]=sum(price)
        menu["status"]="delivered"

        data.append(menu)

    query2="SELECT * FROM cancelled_orders WHERE email_of_consumer="+email+" AND date="+date
    cancelledOrders= await  database.fetch_all(query=query2)
    for i in range(len(cancelledOrders)):
        menu={}
        menu["outlet_name"]=cancelledOrders[i][12]
        menu["items"]=cancelledOrders[i][9]
        menu["quantities"]=cancelledOrders[i][10]
        price=list(map(int,deliveredOrders[i][11].split("_")[:-1]))
        menu["total"]=sum(price)
        menu["status"]="cancelled"

        data.append(menu)

    return data

@app.post("/student/postRating")
async def postRating(order:schemas.StudentRatingSchema,db:Session=Depends(get_db)):
    exists=db.query(models.StudentRating).filter(models.StudentRating.consumer_email==order.consumer_email).first()
    if exists:
        for i in range(len(order.rated_items)):
            itemexists=db.query(models.StudentRating).filter(models.StudentRating.item==order.rated_items[i]["item"],models.StudentRating.outlet_name==order.rated_items[i]["outletName"]).first()
            if itemexists:
                itemexists.rating=order.rated_items[i]["rating"]
                db.commit()
            else:
                newdata=models.StudentRating()
                newdata.item=order.rated_items[i]["item"]
                newdata.rating=order.rated_items[i]["rating"]
                newdata.outlet_name=order.rated_items[i]["outletName"]
                newdata.consumer_email=order.consumer_email
                db.add(newdata)
                db.commit()
    else:
         for i in range(len(order.rated_items)):
            

            newdata=models.StudentRating()
            newdata.item=order.rated_items[i]["item"]
            newdata.rating=order.rated_items[i]["rating"]
            newdata.outlet_name=order.rated_items[i]["outletName"]
            newdata.consumer_email=order.consumer_email
            db.add(newdata)
            db.commit()

@app.get("/student/get-calories-internalvendor/{email}/{date}")
async def get_calories_internalvendor(email:str, date:str,db:Session=Depends(get_db)):
    email="'{}'".format(email)
    date="'{}'".format(date)
    query1="SELECT * FROM delivered_orders WHERE email_of_consumer="+email+" AND date="+date
    deliveredOrders= await  database.fetch_all(query=query1)
    items=[] 
    quantities=[]
    items=deliveredOrders[0][9].split("_")[:-1]
    quantities=deliveredOrders[0][10].split("_")[:-1]
    print(items)
    print(quantities)
    totalCalorie=0
    for i in range(len(items)):
        item_value = "'{}'".format(items[i])
        query2="SELECT * FROM calorie_info WHERE items=="+item_value
        calorieinfo= await  database.fetch_one(query=query2)
         
        calorie_value = int(calorieinfo[2])
        print(calorie_value)
        totalCalorie=totalCalorie+(calorie_value*int(quantities[i]))
     
    print(totalCalorie)    
    return totalCalorie    


