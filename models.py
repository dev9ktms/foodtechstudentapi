from sqlalchemy import Column, Integer, String, ForeignKey,Text,BigInteger
from sqlalchemy.orm import relationship,Mapped
from database import Base

class Students(Base):
    __tablename__ = "signup_students"

    # id = Column(BigInteger,index=True)
    name = Column(String(50))
    Age = Column(BigInteger)
    Gender = Column(String(50))
    Address_line_1 = Column(String(50))
    Address_line_2 = Column(String(50))
    City = Column(String(50))
    State = Column(String(50))
    Pincode= Column(BigInteger)
    Country = Column(String(50))
    Phone = Column(BigInteger)
    email = Column(String(50),nullable=False,primary_key=True)
    institute= Column(String(50))

 

class StudentOrder(Base):
    __tablename__="studentorders_internalvendor"
    id = Column(BigInteger,index=True, primary_key=True)
    name = Column(String(50))
    Address_line_1 = Column(String(50))
    Address_line_2 = Column(String(50))
    Phone = Column(BigInteger)
    date = Column(String(50))
    email = Column(String(50))
    institute= Column(String(50))
    items=Column(String(50))
    quantities=Column(String(50))
    prices=Column(String(50))
    outlet_name=Column(String(50))


class Consumption(Base):
    __tablename__ = "food_consumed"
   
    student_phone = Column(BigInteger,primary_key=True,nullable=False) 
    date = Column(String(50))
    type = Column(String(50))
    total_calories = Column(BigInteger)

 

class SessionModel(Base):
    __tablename__="student_session"
    
    sessionId = Column(Text(), primary_key=True)
    email = Column(String(50))

class ConsumptionHistory(Base):
    __tablename__="consumption_history"
    id = Column(BigInteger,index=True, primary_key=True)
    user_id = Column(String(50))
    date = Column(String(50))
    consumed= Column(String(50))
    mess_name = Column(String(50))
    institute=Column(String(50))
    calories_breakfast=Column(BigInteger)
    calories_lunch=Column(BigInteger)
    calories_snacks=Column(BigInteger)
    calories_dinner=Column(BigInteger)

class StudentRating(Base):
    __tablename__ = 'student_rating'
    id = Column(BigInteger,index=True, primary_key=True)
    consumer_email = Column(String(50))
    outlet_name = Column(String(50))
    item=Column(String(50))
    rating = Column(BigInteger)
    


    



