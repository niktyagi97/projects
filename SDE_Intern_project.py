import tkinter as tk
from twilio.rest import Client
import smtplib
import mysql.connector
import re
from datetime import datetime

regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
fields = 'Guest_Name', 'Guest_Email_ID', 'Guest_Phone_Number', 'Host_Name', 'Host_Email_ID', 'Host_Phone_Number'
entries = []
exit_ = []

def check_valid_mail(email):   
    if(re.search(regex,email)):  
        return True 
    else:  
        return False

def check_valid_number(s): 
    Pattern = re.compile("(0/91)?[6-9][0-9]{9}") 
    return Pattern.match(s)

def inform_host():
    msg = []
    for i in range(0,3):
        field = entries[i][0]
        data = entries[i][1].get()
        msg.append((field,data))
    itr = 0
    ms = ""
    for i in msg:
        for k in i:
            itr = itr+1
            if itr%2==1:
                ms = ms + str(k)+": "
            else:
                ms = ms + str(k)+"\n"
    mail = entries[4][1].get()
    number = entries[5][1].get()
    mail_and_text(mail,int(number),ms,1)

def mail_and_text(recipient_mail,recipient_number,message,flag):
    message = "\n" + message
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.starttls() 
    s.login("SENDER_MAIL_ID(xxx@gmail.com)", "SENDER MAIL_ID_PASSWORD")
    s.sendmail("SENDER_MAIL_ID(xxx@gmail.com)", recipient_mail,message)
    s.quit()
    account_sid = 'ACXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
    auth_token = 'PASSWORD'
    if flag==1:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(to = "+"+str(recipient_number),from_="+919027110314", body =message)
        print(msg.sid)


def combine_funcs(*funcs):
    def combined_func(*args, **kwargs):
        for f in funcs:
            f(*args, **kwargs)
    return combined_func

def error_pop():
    thirdwindow = tk.Tk()
    T = tk.Text(thirdwindow, height=2, width=30)
    T.pack()
    T.insert(tk.END, "Enter Correct Credentials\n")
    b6 = tk.Button(thirdwindow, text='Ok', command=thirdwindow.destroy)
    b6.pack(side=tk.LEFT, padx=5, pady=5)
    return

def chk_and_save():
    mydb = mysql.connector.connect(host="localhost",user="root",passwd="root@123",database="sys")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM Emp_Database")
    myresult = mycursor.fetchall()
    mycursor.execute("SELECT COUNT(*) FROM Emp_Database")
    temp = mycursor.fetchall()
    empid = 0
    if entries[5][1].get()!="":
        mycursor.execute("SELECT Emp_ID FROM Emp_Database where "+entries[5][1].get()+"=PhoneNo")
        t = mycursor.fetchall()
        empid = t[0][0]
    count = int(temp[0][0])
    flag=0
    for itr in range(0,count):
        if entries[5][1].get()==myresult[itr][2] and entries[4][1].get()==myresult[itr][3] and entries[3][1].get()==myresult[itr][1]:
            flag=1
    if flag==0:
        error_pop()
        return
    if not(check_valid_mail(entries[1][1].get())):
        error_pop()
        return
    if not(check_valid_number(entries[2][1].get())):
        error_pop()
        return
    if entries[0][1].get()=="":
        error_pop()
        return
    mycursor.execute("SELECT COUNT(*) FROM guest_db")
    temp = mycursor.fetchall()
    dateTimeObj = datetime.now()
    timeStr = dateTimeObj.strftime("%H:%M:%S")
    dateStr = dateTimeObj.strftime("%Y-%m-%d")
    mycursor.execute("INSERT INTO guest_db (Guest_id,Name,EmailID,PhoneNo,CheckIn,CheckOut,Date,Host_ID)VALUES('"+str(int(temp[0][0])+1)+"','"+str(entries[0][1].get())+"','"+str(entries[1][1].get())+"','"+str(entries[2][1].get())+"','"+timeStr+"',NULL,'"+dateStr+"','"+str(empid)+"')")
    mycursor.execute("commit")
    inform_host()
    return
    
def make_entry_form(root, fields):
    for field in fields:
        row = tk.Frame(root)
        lab = tk.Label(row, width=20, text=field, anchor='w')
        ent = tk.Entry(row)
        row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        lab.pack(side=tk.LEFT)
        ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        entries.append((field,ent))
    return entries

def make_exit_form(root):
    row = tk.Frame(root)
    lab = tk.Label(row, width=20, text='Guest_ID', anchor='w')
    ent = tk.Entry(row)
    row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
    lab.pack(side=tk.LEFT)
    ent.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
    exit_.append(('Guest_ID', ent))

def pop_guest_id():
    window = tk.Tk()
    mydb = mysql.connector.connect(host="localhost",user="root",passwd="root@123",database="sys")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT COUNT(*) FROM guest_db")
    temp = mycursor.fetchall()
    mycursor.close()
    T = tk.Text(window, height=2, width=30)
    T.pack()
    T.insert(tk.END, "Guest id: " + str(int(temp[0][0])))
    b7 = tk.Button(window, text='OK', command=window.destroy)
    b7.pack(side=tk.LEFT, padx=5, pady=5)
    window.mainloop()
    
def check_in():
    tag = 0
    entries.clear()
    secondwindow = tk.Tk()
    secondwindow.title("Check IN")
    make_entry_form(secondwindow,fields)
    b5 = tk.Button(secondwindow, text='Save Details', command=combine_funcs(chk_and_save,combine_funcs(secondwindow.destroy,pop_guest_id)))
    b5.pack(side=tk.LEFT, padx=5, pady=5)
    secondwindow.mainloop()

def pr():
    mydb = mysql.connector.connect(host="localhost",user="root",passwd="root@123",database="sys")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT COUNT(*) FROM guest_db where (Guest_id = "+str(exit_[0][1].get())+" AND CheckOut IS NULL)")
    temp = mycursor.fetchall()
    if int(temp[0][0]==0):
        error_pop()
        return
    else:
        dateTimeObj = datetime.now()
        mycursor.execute("update guest_db set CheckOut = '"+str(dateTimeObj.strftime("%H:%M:%S"))+"' where Guest_id="+str(exit_[0][1].get()))
        mycursor.execute("commit")
        msg_guest()

def msg_guest():
    g_id = str(exit_[0][1].get())
    mydb = mysql.connector.connect(host="localhost",user="root",passwd="root@123",database="sys")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM guest_db where (Guest_id = "+str(exit_[0][1].get())+" )")
    temp = mycursor.fetchall()
    mycursor.execute("SELECT * FROM emp_database where (Emp_ID = "+str(temp[0][7])+" )")
    t = mycursor.fetchall()
    msg = 'Name: '+str(temp[0][1])+"\nPhone Number: "+str(temp[0][3])+"\nCheck In Time: "+str(temp[0][4])+"\nCheck Out Time: "+str(temp[0][5])+"\nHost Name: "+str(t[0][1])+"\nAddress Visited: "+str(t[0][4])
    mail_and_text(temp[0][2],int(temp[0][3]),msg,0)
    
def check_out():
    secondwindow = tk.Tk()
    exit_.clear()
    make_exit_form(secondwindow)
    b4 = tk.Button(secondwindow, text='Check_Out', command=combine_funcs(pr,secondwindow.destroy))
    b4.pack(side=tk.LEFT, padx=5, pady=5)
    secondwindow.mainloop()
    
if __name__ == '__main__':
    firstwindow = tk.Tk()
    firstwindow.title("Entry Management System")
    b1 = tk.Button(firstwindow, text='Check_In', command=check_in)
    b1.pack(side=tk.LEFT, padx=5, pady=5)
    b2 = tk.Button(firstwindow, text='Check_Out', command=check_out)
    b2.pack(side=tk.LEFT, padx=5, pady=5)
    b3 = tk.Button(firstwindow, text='Close', command=firstwindow.destroy)
    b3.pack(side=tk.LEFT, padx=5, pady=5)
    firstwindow.mainloop()
    
