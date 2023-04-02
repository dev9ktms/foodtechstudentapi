from pydantic import BaseModel, Field

class Student(BaseModel):
    institute:str=Field()
    Age:int = Field()
    Gender: str = Field(min_length=1)
    Address_line_1: str = Field(min_length=1,max_length=100)
    Address_line_2: str = Field(max_length=100)
    City: str = Field(min_length=1)
    State: str = Field(min_length=1)
    Pincode: int = Field()
    Country: str = Field(min_length=1)
    Phone: int = Field()
    email: str = Field(min_length=1)


class FoodConsumption(BaseModel):
    student_phone: int = Field()
    date: str= Field(min_length=1)
    type: str= Field(min_length=1)
    total_calories: int= Field()

class StudentOrderSchema (BaseModel):
    user_id: str= Field(min_length=1)
    outlet_name:str = Field(min_length=1)
    prices: list = Field ()
    quantities: list = Field ()
    items: list = Field ()
    date:str=Field()


class ConsumptionHistorySchema(BaseModel):
    user_id: str= Field(min_length=1)
    date: str= Field(min_length=1)
    mess_name: str= Field(min_length=1)
    consumed: list =Field()
    institute: str= Field(min_length=1)

class StudentRatingSchema(BaseModel):
    consumer_email:str = Field(min_length=1)
    rated_items:list = Field()