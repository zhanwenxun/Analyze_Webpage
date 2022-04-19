#coding=utf-8
#import os
import csv
import json
import numpy as np
import timeit
from matplotlib import pyplot as plt
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pypinyin


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =======================DATA=========================
# data = pd.read_csv("submit_data.csv")


"""
=================== Body =============================
"""

class FileName(BaseModel):
    content: str

# == == == == == == == == == API == == == == == == == == == == =

# # show four genres
@app.post("/api/data")
def plot_figure(filename: FileName):
    # 前端传过来的数据文件名
    print(filename.content)
    print(type(filename.content))
    if '.csv' in filename.content:
        df = pd.read_csv(''+filename.content)
    if '.xlsx' in filename.content:
        df = pd.read_excel(''+filename.content)
    start=timeit.default_timer()
    df = df[df['date'] != '1970-01-01']
    df['date'] = pd.to_datetime(df['date'])
    df = df.drop(['category1', 'category2', 'category3'], axis=1)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    sale_by_quarter(df)
    sale_by_month(df)
    sale_by_date(df)
    sale_by_hour(df)
    gender_rate(df)
    age_distribution(df)
    RFM_model(df)
    location_dist = []
    location_dist = location(df,location_dist)
    runtime=timeit.default_timer()-start
    print(runtime)
    print(location_dist)
    return json.dumps(location_dist)


def sale_by_quarter(df):
    sale_by_quarter = df['quarter'].value_counts().sort_index()
    plt.figure(figsize=(8, 5))
    plt.title("sale by quarter",size=20)
    plt.xlabel("quarter",size=20)
    plt.ylabel("sales volume",size=20)
    for i in range(len(sale_by_quarter.index)):
        plt.text(sale_by_quarter.index[i], sale_by_quarter.values[i], str(sale_by_quarter.values[i]),size=10)
    plt.plot(sale_by_quarter.index, sale_by_quarter.values)
    plt.savefig('images/sale_by_quarter.jpg')
    plt.close()

def sale_by_month(df):
    sale_by_month = df['month'].value_counts().sort_index()

    plt.figure(figsize=(20, 13))
    plt.title("sale by month",size=40)
    plt.xlabel("month",size=40)
    plt.ylabel("sales volume",size=40)
    for i in range(len(sale_by_month.index)):
        plt.text(sale_by_month.index[i], sale_by_month.values[i], str(sale_by_month.values[i]),size=20)
    plt.plot(sale_by_month.index, sale_by_month.values)
    plt.savefig('images/sale_by_month.jpg')
    plt.close()

def get_month(x):
    if x == 1 :
        return 'January'
    if x == 2 :
        return 'February'
    if x == 3 :
        return 'March'
    if x == 4 :
        return 'April'
    if x == 5 :
        return 'May'
    if x == 6 :
        return 'June'
    if x == 7 :
        return 'July'
    if x == 8 :
        return 'August'
    if x == 9 :
        return 'September'
    if x == 10 :
        return 'October'
    if x == 11 :
        return 'November'
    if x == 12 :
        return 'December'

def sale_by_date(df):
    sale_by_month = df['month'].value_counts().sort_index()
    for i in range(len(sale_by_month.index)):
        df2 = df[df['month'] == sale_by_month.index[i]]
        sale_by_date = df2['date'].value_counts().sort_index()
        print(sale_by_date)

        plt.figure(figsize=(20, 13))
        plt.title("sale by date in "+get_month(sale_by_month.index[i]),size=40)
        plt.xlabel("date",size=40)
        plt.ylabel("sales volume",size=40)
        for j in range(len(sale_by_date.index)):
            plt.text(sale_by_date.index[j], sale_by_date.values[j], str(sale_by_date.values[j]),size=20)
        plt.plot(sale_by_date.index, sale_by_date.values)
        plt.savefig('images/sale_by_date' + str(sale_by_month.index[i]) + '.jpg')
        plt.close()

def sale_by_hour(df):
    df[['sale_hour', 'sale_minute', 'sale_second']] = df['time'].str.split(':', 2, expand=True)
    df = df.drop(['sale_minute', 'sale_second'], axis=1)
    sale_by_hour = df['sale_hour'].value_counts().sort_index()

    plt.figure(figsize=(20, 13))
    plt.title("sale by hour",size=40)
    plt.xlabel("hour",size=40)
    plt.ylabel("sales volume",size=40)
    for i in range(len(sale_by_hour.index)):
        plt.text(sale_by_hour.index[i], sale_by_hour.values[i], str(sale_by_hour.values[i]),size=20)
    plt.plot(sale_by_hour.index, sale_by_hour.values)
    plt.savefig('images/sale_by_hour.jpg')
    plt.close()

def gender_rate(df):
    df['gender'] = df.sex.map(lambda x: 'female' if x == '女' else 'male')
    gender_rate = df['gender'].value_counts().sort_index()
    # print(gender_rate)
    plt.figure(figsize=(20, 13))
    plt.title("gender rate",size=40)
    plt.xlabel("gender",size=40)
    plt.ylabel("sales volume",size=40)
    for i in range(len(gender_rate.index)):
        plt.text(gender_rate.index[i], gender_rate.values[i], str(gender_rate.values[i]), size=20)
    plt.bar(gender_rate.index, gender_rate.values, width=0.4, color=['pink', 'lightskyblue'])
    # plt.show()
    plt.savefig('images/gender_rate.jpg')
    plt.close()

def age_distribution(df):
    df['age_range'] = df.age.map(lambda x: '0-18' if x < 19
    else '19-24' if x < 25 else '25-36' if x < 37
    else '37-48' if x < 49 else 'above 49')
    age_distribution = df['age_range'].value_counts().sort_index()
    print(age_distribution)
    plt.pie(
        x=[age_distribution.values[0], age_distribution.values[1], age_distribution.values[2],
           age_distribution.values[3], age_distribution.values[4]],
        labels=[age_distribution.index[0], age_distribution.index[1], age_distribution.index[2],
                age_distribution.index[3], age_distribution.index[4]],
        colors=['lightskyblue', 'red', 'green', 'yellow', 'violet'],
        explode=[0, 0.05, 0.03, 0, 0],
        autopct='%1.1f%%',
        radius=1,
    )
    plt.title('age distribution',size=40)
    # plt.show()
    plt.savefig('images/age_distribution.jpg')
    plt.close()

def RFM_define(x):
    if x['R_v']==0 and x['F_v']==0 and x['M_v']==0:
        return 'normal-persuade-customer'
    if x['R_v']==0 and x['F_v']==0 and x['M_v']==1:
        return 'important-persuade-customer'
    if x['R_v']==0 and x['F_v']==1 and x['M_v']==0:
        return 'normal-maintain-customer'
    if x['R_v']==0 and x['F_v']==1 and x['M_v']==1:
        return 'important-maintain-customer'
    if x['R_v']==1 and x['F_v']==0 and x['M_v']==0:
        return 'normal-develop-customer'
    if x['R_v']==1 and x['F_v']==0 and x['M_v']==1:
        return 'important-develop-customer'
    if x['R_v']==1 and x['F_v']==1 and x['M_v']==0:
        return 'normal-central-customer'
    if x['R_v']==1 and x['F_v']==1 and x['M_v']==1:
        return 'important-central-customer'

def RFM_model(df):
    df['now'] = df['date'].max()
    df['R_value'] = df['now'] - df['date']
    model_value = df.groupby('user_id').agg({'R_value': 'min', 'date': 'count', 'price': 'sum'})
    model_value.rename(columns={'R_value': 'Recency', 'date': 'num_order', 'price': 'pay_total'}, inplace=True)
    recency_mean=model_value['Recency'].mean()
    frequency_mean=model_value['num_order'].mean()
    monetary_mean=model_value['pay_total'].mean()
    model_value['R_v'] = model_value['Recency'].apply(lambda x: 1 if x < recency_mean else 0)
    model_value['F_v'] = model_value['num_order'].apply(lambda x: 1 if x > frequency_mean else 0)
    model_value['M_v'] = model_value['pay_total'].apply(lambda x: 1 if x > monetary_mean else 0)
    model_value['RFM_definition'] = model_value.apply(RFM_define, axis=1)
    RFM_distribution = model_value['RFM_definition'].value_counts()

    plt.pie(
        x=[RFM_distribution.values[0], RFM_distribution.values[1], RFM_distribution.values[2],
           RFM_distribution.values[3],
           RFM_distribution.values[4], RFM_distribution.values[5], RFM_distribution.values[6],
           RFM_distribution.values[7]],
        labels=[RFM_distribution.index[0], RFM_distribution.index[1], RFM_distribution.index[2],
                RFM_distribution.index[3],
                RFM_distribution.index[4], RFM_distribution.index[5], RFM_distribution.index[6],
                RFM_distribution.index[7]],
        colors=['lightskyblue', 'red', 'green', 'yellow', 'violet', 'cyan', 'peachpuff', 'springgreen'],
        autopct='%1.1f%%',
        radius=1,
    )
    plt.title('RFM distribution',size=40)
    # plt.show()
    plt.savefig('images/RFM_distribution.jpg')
    plt.close()

def pypinyin_trans(x):
    a = pypinyin.pinyin(x,style=pypinyin.FIRST_LETTER)
    b = []
    for i in range(len(a)):
        b.append(str(a[i][0]).upper())
    c = ''.join(b)
    return c

def location(df,location_dist):
    df['location'] = df['local'].apply(pypinyin_trans)
    location_distribution = df['location'].value_counts()
    for i in range(len(location_distribution)):
        location_dist.append({"id": 'CN-' + str(location_distribution.index[i]), "value": int(location_distribution.values[i])})
    # print(location_dist)
    return location_dist