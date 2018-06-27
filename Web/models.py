# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
#from django.db import connection
import sqlite3

connection = sqlite3.connect('db.sqlite3',check_same_thread=False)
cur = connection.cursor()

def db_insert_classroom(id_,loc_,cap_,m_media_,camp_,remark_):
    if int(id_) in get_classroom_ids():
        return False
    res = cur.execute('''
    insert into CLASSROOM (ID,LOCATION,CAPACITY,MULTIMEDIA,CAMPUS,REMARK) VALUES (%d,"%s",%d,"%s","%s","%s");
   '''%(int(id_),loc_,int(cap_),m_media_,camp_,remark_))

    connection.commit()
    return True

def db_update_classroom(tuple):
    print(tuple)
    if int(tuple[0]) not in get_classroom_ids():
        return False
    else:
        return cur.execute('UPDATE CLASSROOM set  LOCATION = "%s", CAPACITY = %d,MULTIMEDIA = "%s",CAMPUS="%s",REMARK="%s" where id = %d'
                           %(tuple[1],int(tuple[2]),tuple[3],tuple[4],tuple[5],int(tuple[0])))

def db_delete(tuple):
    if int(tuple[0]) not in get_classroom_ids():
        return False
    else:
        return cur.execute('delete  from CLASSROOM where  ID = %d'%int(tuple[0]))

def db_delete_all():
    cur.execute('delete from CLASSROOM')

    connection.commit()

# returns a list of list
def get_classroom_info():
    classroom_info = cur.execute('''
        select * from CLASSROOM 
    ''')
    #print('class info: ',classroom_info)
    return classroom_info

#return a list of dicts
def get_classroom_table():
    info = get_classroom_info()
    table = []
    for line in info:
        table.append({
            'id':line[0],
            'loc':line[1],
            'cap':line[2],
            'multimedia':line[3],
            'campus':line[4],
            'remark':line[5]
            }
        )
    return table

def get_classroom_ids():
    table = get_classroom_info()
    ids = []
    for line in table:
        ids.append(line[0])
    print('ids: ',ids)
    return ids

'''
    get courses data
'''
def getData(type,name):
    if str(type) == 'teacher':
        data_1 = Classtable.objects.filter(teacher_name = name)
        data_2 = dataDeal(data_1)
    elif str(type) == 'student':
        data_1 = Classtable.objects.all()
        data_2 = dataDeal(data_1)
        data_2 = data_2[0:min(9,len(data_2))]
    return data_2
'''
    if str(type) == "teacher":
        sql = "select * from Classtable where teacher_name = \'"
        sql = sql + str(name) + "\';"
    elif str(type) == "student":
        sql = "select * from Classtable;"
    cur.execute(sql)
    data_1 = cur.fetchall()
    data_2 = dataDeal(data_1)
    if str(type) == "student":
        data_2 = data_2[0:min(9,len(data_2))]
'''

def dataDeal(data_1):
    new_data = []
    for item in data_1:
        temp = []
        temp.append(item.course_identity)
        temp.append(item.course_name)
        temp.append(item.teacher_name)
        temp.append(item.course_time_1)
        temp.append(item.classroom_name_1)
        new_data.append(temp)
        if item.course_period == 2:
            temp = []
            temp.append(item.course_identity)
            temp.append(item.course_name)
            temp.append(item.teacher_name)
            temp.append(item.course_time_2)
            temp.append(item.classroom_name_2)
            new_data.append(temp)
    return new_data
'''
    new_data = []
    for item in data_1:
        temp = []
        temp.append(item[1])
        temp.append(item[2])
        temp.append(item[3])
        temp.append(item[6])
        temp.append(item[10])
        new_data.append(temp)
        if item[5] == 2:
            temp = []
            temp.append(item[1])
            temp.append(item[2])
            temp.append(item[3])
            temp.append(item[7])
            temp.append(item[11])
            new_data.append(temp)
    return new_data
'''

'''
    Scheduler and Database
'''

import numpy as np
from scipy.optimize import linprog


# Create your models here.

class Classroom(models.Model):
    identity = models.IntegerField()
    name = models.CharField(max_length = 30)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

class Class(models.Model):
    identity = models.IntegerField()
    name = models.CharField(max_length = 30)
    teacher_name = models.CharField(max_length = 30)
    capacity = models.IntegerField()
    period = models.IntegerField()

    def __str__(self):
        return self.name

class Classtable(models.Model):
    identity = models.IntegerField()
    course_identity = models.IntegerField()
    course_name = models.CharField(max_length = 30)
    teacher_name = models.CharField(max_length = 30)
    course_capacity = models.IntegerField() 
    course_period = models.IntegerField() # how many course periods there are
    course_time_1 = models.IntegerField() # the first course time 
    course_time_2 = models.IntegerField(null = True) # the second course time 
    classroom_identity_1 = models.IntegerField()
    classroom_identity_2 = models.IntegerField(null = True)
    classroom_name_1 = models.CharField(max_length = 30)
    classroom_name_2 = models.CharField(max_length = 30, null = True)
    classroom_capacity_1 = models.IntegerField()
    classroom_capacity_2 = models.IntegerField(null = True)
    
    def __str__(self):
        return self.course_name


def scheduler():
    class_size = len(Class.objects.all())
    classroom_size =  len(Classroom.objects.all())
    class_period = 10 # There are 2 * 5 periods for a class day
    # x(i,j,k): class i, classroom j, periods k for a class
    x = np.zeros((class_size, classroom_size, class_period), dtype = np.int)
    #class_period for every class
    a = np.array(np.concatenate(np.array(list(Class.objects.values_list('period')))))
    #c(i,j): the capacity of classroom j divided by the number of students enrolled in course i.  
    ccc = np.zeros((class_size, classroom_size, class_period), dtype = np.float)

    count = 0
    for i in range(class_size):
        for j in range(classroom_size):
            class_people = Class.objects.filter(identity = i).values('capacity')[0]['capacity']
            class_room_people = Classroom.objects.filter(identity = j).values('capacity')[0]['capacity']
            if class_people > class_room_people:
                count += 1
            temp = class_people / class_room_people
            for k in range(class_period):
                ccc[i,j,k] = temp

    T_size = count
    #print(x)
    #print(a)
    #print(c)
    c = np.concatenate(ccc) 
    #print(c)
    A_eq = np.zeros((class_size, classroom_size, class_period, class_size ), dtype = np.int)
    A_ub = np.zeros((class_size, classroom_size, class_period, classroom_size * class_period), dtype = np.int)

    b_eq = np.array(a)
    temp = np.zeros((T_size))
    b_eq = np.append(b_eq, temp)

    temp = np.ones((classroom_size, class_period))
    b_ub = np.array(temp)

    # calculate A_eq
    count = 0 
    temp = np.zeros((class_size, classroom_size, class_period, T_size))
    for i in range(class_size):
        A_eq[i,:,:,i] = np.ones((classroom_size, class_period))
    for i in range(class_size):
        for j in range(classroom_size):
            class_people = Class.objects.filter(identity = i).values('capacity')[0]['capacity']
            #class_people = Class.objects.filter(identity = 1)[0].capacity
            class_room_people = Classroom.objects.filter(identity = j).values('capacity')[0]['capacity']
            if(class_people > class_room_people):
                temp[i, j, :, count] = np.ones((class_period))
                count += 1
    A_eq = np.append(A_eq, temp, axis = 3)

    # calculate A_ub
    count = 0
    for j in range(classroom_size):
        for k in range(class_period):
            A_ub[:, j, k, count] = np.ones((class_size))
            count += 1

    c = c.reshape(-1)
    A_eq = np.concatenate(A_eq).reshape(-1, class_size + T_size ).T
    A_ub = np.concatenate(A_ub).reshape(-1, classroom_size * class_period).T      
    #b_eq = np.concatenate(b_eq)
    b_ub = np.concatenate(b_ub)

    '''
    print(c.shape)
    print(A_eq.shape)
    print(A_ub.shape)
    print(b_eq.shape)
    print(b_ub.shape)
    '''

    r = linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=tuple([(0,1)]* (class_size * classroom_size * class_period)))

    #print(r)

    #print(r.x)
    if(r.success):
        reshape_x = r.x.reshape(class_size, classroom_size, class_period)
        #print(reshape_x)
        count = 0
        for i in range(class_size):
            is_class = 0
            class_table_obj = Classtable(identity = count)
            for j in range(classroom_size):
                for k in range(class_period):
                    if reshape_x[i,j,k] == 1:
                        if is_class == 0:
                            class_table_obj.identity = count
                            class_table_obj.course_identity = Class.objects.filter(identity = i)[0].identity
                            class_table_obj.course_name = Class.objects.filter(identity = i)[0].name
                            class_table_obj.teacher_name = Class.objects.filter(identity = i)[0].teacher_name
                            class_table_obj.course_capacity = Class.objects.filter(identity = i)[0].capacity
                            class_table_obj.course_period = Class.objects.filter(identity = i)[0].period
                            class_table_obj.course_time_1 = k
                            class_table_obj.classroom_identity_1 = Classroom.objects.filter(identity = j)[0].identity
                            class_table_obj.classroom_name_1 = Classroom.objects.filter(identity = j)[0].name
                            class_table_obj.classroom_capacity_1 = Classroom.objects.filter(identity = j)[0].capacity
                            is_class = 1
                            count += 1
                        else :
                            class_table_obj.course_time_2 = k
                            class_table_obj.classroom_identity_2 = Classroom.objects.filter(identity = j)[0].identity
                            class_table_obj.classroom_name_2 = Classroom.objects.filter(identity = j)[0].name
                            class_table_obj.classroom_capacity_2 = Classroom.objects.filter(identity = j)[0].capacity
            class_table_obj.save()
        
        print(Classtable.objects.all().values())

