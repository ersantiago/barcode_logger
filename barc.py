import datetime
import shutil
from tkinter import *
import os
import socket

# ===============================================================================================#
# insert code for spreadsheet sync
import pygsheets
import ast

# VARIABLES
site_target = 'INSULAR'
it_gsheet = 'https://docs.google.com/spreadsheets/d/1OXuBnhvfe2_iC-xkrdtadMtVv8TH9TcIscrUCZeKM2Q/edit#gid=1939728290'
path_cred = 'C:\\Scripts\\barc\\cfg\\IT-DA-9a643fc39003.json'
maindir = "C:\\Scripts\\barc"
#path_cred = '/mnt/share/scripts/admin_scripts/api/IT-DA-9a643fc39003.json'
#prdtck_file = '/opt/lampp/htdocs/ftp_xims/prod/prdbdir/prd_table.list'
#maindir = "/home/xinyx/barc/db"

print('Initialize database sync...')

bcdb = os.path.join(maindir, 'db', 'barcode_db.csv')
bcdb_all = os.path.join(maindir, 'db', 'barcode_db_full.csv')
tmp_file = os.path.join(maindir, 'db', 'tmp_db.csv')

# Load Local DB
if not os.path.exists(bcdb):
    "Create dummy file"
    open(bcdb,'+a').close()

dblocal_raw = open(bcdb, 'r').read().splitlines()[1:]
dblocal_dct = {}
for line in dblocal_raw:
    bc, fname, user, cps = line.split(',')
    udct = {}
    udct['fname'] = fname
    udct['user'] = user
    udct['cps'] = cps
    dblocal_dct[bc] = udct

# Load Config IT Sheets
gc = pygsheets.authorize(service_file=path_cred)
wks = gc.open_by_url(it_gsheet)
sheet = wks.worksheet_by_title('barcode')
dbcfg_raw = sheet.get_values('A4', 'E500')

dbcfg_dct = {}
for line in dbcfg_raw:
    tag,bc,user,fname,site = line
    if site == site_target:
        udct = {}
        udct['fname'] = fname
        udct['user'] = user
        udct['site'] = site
        try:
            udct['cps'] = dblocal_dct[bc]['cps']
        except:
            udct['cps'] = 'OUT'
        dbcfg_dct[bc] = udct

# Create Dictionary

'''
nfs_bcdb = '/mnt/share/scripts/db/barcode_db.csv'
nfs_bcdb_all = '/mnt/share/scripts/db/barcode_db_full.csv'
'''

# reconstruct init_csv
init_csv = []
for entry in dbcfg_dct:
    cps = dbcfg_dct[entry]['cps']
    user = dbcfg_dct[entry]['user']
    fname = dbcfg_dct[entry]['fname']
    bc = entry
    merge = ','.join([bc, fname, user, cps])
    init_csv.append(merge)
head_csv = 'id_number,full_name,username,status'
'''
init_csv = open(bcdb, 'r').read().splitlines()
head_csv = init_csv[0]
init_csv = init_csv[1:]

dbdct = {}
for i in range(len(init_csv)):
    csv_cps = init_csv[i].split(',')[-1]
    csv_bc = init_csv[i].split(',')[0]
    dbdct[csv_bc] = csv_cps
'''

#
# ===============================================================================================#

master = Tk()
master.minsize(width=370, height=80)
master.columnconfigure(1, weight=1)
#master.attributes('-fullscreen', True)
master.attributes('-fullscreen', False)

# ======================================================================================================== #
#                                                Functions                                                 #
# ======================================================================================================== #

def internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False

def updstat(current_status):
    label_stat.configure(text=current_status)

def enterkey(event):

    # Get input and corresponding DTR
    input_bc = bcin.get()
    input_bc = input_bc[0:-1]
    x = datetime.datetime.now()
    dtr = x.strftime("%b%d_%G_[%R]")
    print(input_bc)

    # Clear Box
    e1.delete(0, 'end')

    try:
        '''
        init_csv = open(bcdb, 'r').read().splitlines()
        head_csv = init_csv[0]
        init_csv = init_csv[1:]

        mydct = {}
        for i in range(len(init_csv)):
            csv_cps = init_csv[i].split(',')[-1]
            csv_bc = init_csv[i].split(',')[0]
            mydct[csv_bc] = csv_cps
        '''
        mydct = dbcfg_dct.copy()
        if mydct[input_bc]['cps'] == 'OUT':
            fg_cps = '#ffffff'
            bg_cps = '#136986'
            labels_cps[input_bc].configure(bg=bg_cps, fg=fg_cps, text='IN')

            cps_dict[input_bc] = 'IN'

            current_status = 'Latest Scan : [' + input_bc + ']   ' + user_dict[input_bc] + '   ' + cps_dict[input_bc] + '   ' + dtr
            updstat(current_status)
            label_stat.configure(bg=bg_cps)
            mframe.configure(background=bg_cps)

            write_tmp = open(tmp_file, 'w')
            write_tmp.write(head_csv + '\n')

            # reconstruct init_csv
            init_csv = []
            for entry in dbcfg_dct:
                cps = dbcfg_dct[entry]['cps']
                user = dbcfg_dct[entry]['user']
                fname = dbcfg_dct[entry]['fname']
                bc = entry
                merge = ','.join([bc,fname,user,cps])
                init_csv.append(merge)

            for i in range(len(init_csv)):
                if input_bc in init_csv[i]:
                    splitv = init_csv[i].split(',')[:-1]
                    splitv.append('IN')
                    init_csv[i] = ','.join(splitv)
                    print(init_csv[i])
                write_tmp.write(init_csv[i] + '\n')
            write_tmp.close()

            # Write to Database
            try:
                csvformat = ','.join([input_bc, dtr, cps_dict[input_bc], '\n'])
                bcdb_write = open(bcdb_all, 'a+')
                bcdb_write.write(csvformat)
                bcdb_write.close()

            except:
                print('Unable to dump to database, file is possibly locked.')

            try:
                shutil.move(tmp_file, bcdb)
                shutil.copy(bcdb, nfs_bcdb)
                shutil.copy(bcdb_all, nfs_bcdb_all)
            except:
                print('Database overwrite unsuccessful')

        elif mydct[input_bc]['cps'] == 'IN':
            fg_cps = '#ffffff'
            bg_cps = '#CC5933'
            labels_cps[input_bc].configure(bg=bg_cps, fg=fg_cps, text='OUT')

            cps_dict[input_bc] = 'OUT'

            current_status = 'Latest Scan : [' + input_bc + ']   ' + user_dict[input_bc] + '   ' + cps_dict[input_bc] + '   ' + dtr
            updstat(current_status)
            label_stat.configure(bg=bg_cps)
            mframe.configure(background=bg_cps)

            write_tmp = open(tmp_file, 'w')
            write_tmp.write(head_csv + '\n')
            for i in range(len(init_csv)):
                if input_bc in init_csv[i]:
                    splitv = init_csv[i].split(',')[:-1]
                    splitv.append('OUT')
                    init_csv[i] = ','.join(splitv)
                write_tmp.write(init_csv[i] + '\n')
            write_tmp.close()

            # Write to Database
            try:
                csvformat = ','.join([input_bc, dtr, cps_dict[input_bc], '\n'])
                bcdb_write = open(bcdb_all, 'a+')
                bcdb_write.write(csvformat)
                bcdb_write.close()
            except:
                print('Unable to dump to database, file is possibly locked.')

            try:
                shutil.move(tmp_file, bcdb)
                shutil.copy(bcdb, nfs_bcdb)
                shutil.copy(bcdb_all, nfs_bcdb_all)
            except:
                print('Database overwrite unsuccessful')

        else:
            print('Error handling')
    except:
        print('ID number not recognized')
        current_status = 'Latest Scan : [' + input_bc + ']   barcode ID number not recognized'
        updstat(current_status)
        bg_cps = 'gray'
        label_stat.configure(bg=bg_cps)
        mframe.configure(background=bg_cps)


# ======================================================================================================== #
#                                                Tkinter GUI                                               #
# ======================================================================================================== #

# *** Input Files Section
hframe = Frame(master)
mframe = Frame(master)
fframe = Frame(master)

bg_hframe = '#004157'
bg_mframe = '#004157'

hframe.configure(background=bg_hframe, borderwidth=3, relief=GROOVE, pady=3, padx=3)
mframe.configure(background=bg_mframe, borderwidth=3, relief=GROOVE, pady=3, padx=3)
fframe.configure(borderwidth=3, relief=GROOVE, pady=3, padx=3)

hframe.grid(row=0, column=1, columnspan=10, sticky=W+E)
mframe.grid(row=1, column=1, columnspan=10, sticky=W+E)
fframe.grid(row=2, column=1, columnspan=10, sticky=W+E)

# first frame
Label(hframe, text="Barcode Scan Input: ", font="Calibri 15 bold", fg="white",  bg=bg_hframe, height=1).grid(row=0, sticky=W)

bcin = StringVar()
e1 = Entry(hframe, font="Calibri 17", fg="black", width=21, textvariable=bcin)
e1.grid(row=0, column=1, sticky=W+E, padx=5, pady=3)
e1.focus_set()

# second frame
label_stat = Label(mframe, text="Latest Scan : None", font="Calibri 13 italic", fg="white", bg=bg_mframe, height=1)
label_stat.grid(column=0, sticky=W)


# Subframes #
f1 = Frame(fframe)
f2 = Frame(fframe)
f3 = Frame(fframe)
f4 = Frame(fframe)

f1.pack(side=LEFT, padx=6, pady=0)
f2.pack(side=LEFT, padx=4, pady=0)
f3.pack(side=LEFT, padx=4, pady=0)
f4.pack(side=LEFT, padx=6, pady=0)

fwidth = 59

fframes = [f1, f2, f3, f4]
w_fname = 30
w_user  = 15
w_cps   = 11

bg_header = '#004157'
fg_header = 'white'
for ff in fframes:
    Label(ff, text="Full Name", font="Calibri 12 bold", fg=fg_header, bg=bg_header, height=1, width=w_fname, bd=2, relief=RAISED).grid(row=0, column=0, sticky=E, pady=2)
    Label(ff, text="Username", font="Calibri 12 bold", fg=fg_header, bg=bg_header, height=1, width=w_user, bd=2, relief=RAISED).grid(row=0, column=1, sticky=E, pady=2)
    Label(ff, text="CP Status", font="Calibri 12 bold", fg=fg_header, bg=bg_header, height=1, width=w_cps, bd=2, relief=RAISED).grid(row=0, column=2, sticky=E, pady=2)
labels_bc = {}
labels_fname = {}
labels_user = {}
labels_cps = {}
cps_dict = {}
user_dict = {}

allcnt = len(init_csv)
maxl = 37

for i in range(0,allcnt):
    bc, fname, user, cps = init_csv[i].split(',')
    fname = ' ' + fname
    user = ' ' + user
    rind = i%maxl
    cindx = int(i/maxl)
    if cindx == 0:
        myff = f1
    elif cindx == 1:
        myff = f2
    elif cindx == 2:
        myff = f3
    else:
        myff = f4

    bg_user = '#c9e1e9'
    fg_user = 'black'

    labels_fname[bc] = Label(myff, text=fname, font="Calibri 12", height=1, bg='#c9e1e9', width=w_fname, bd=2, relief=RAISED, anchor="w", pady=2)
    labels_fname[bc].grid(row=rind+1, column=0, sticky=N+E)

    labels_fname[bc].config(highlightbackground='black')

    labels_user[bc]  = Label(myff, text=user, font="Calibri 12", height=1, bg='#c9e1e9', width=w_user, bd=2, relief=RAISED, anchor="w", pady=2)
    labels_user[bc].grid(row=rind+1, column=1, sticky=N+E)

    labels_user[bc].config(highlightbackground='black')

    # defaults
    fg_cps = 'gray'
    bg_cps = 'gray'

    if cps == 'OUT':
        fg_cps = '#ffffff'
        bg_cps = '#CC5933'

    elif cps == 'IN':
        fg_cps = '#ffffff'
        bg_cps = '#136986'


    labels_cps[bc]  = Label(myff, text=cps, font="Calibri 12 bold", bg=bg_cps, fg=fg_cps, height=1, width=w_cps, bd=2, relief=RAISED, pady=2)
    labels_cps[bc].grid(row=rind+1, column=2, sticky=N+E)

    cps_dict[bc] = cps
    user_dict[bc] = user
print(str(cps_dict))

# Fillers
twfill = len(fframes)*maxl

for i in range(allcnt, twfill):
    ffill = fframes[-1]

    rind = i%maxl
    cindx = int(i/maxl)

    Label(ffill, text='', font="Calibri 12 bold", height=1, width=w_fname, bd=1, relief=FLAT).grid(row=rind+1, column=0, sticky=N+E, pady=2)
    Label(ffill, text='', font="Calibri 12 bold", height=1, width=w_user, bd=1, relief=FLAT).grid(row=rind+1, column=1, sticky=N+E, pady=2)
    Label(ffill, text='', font="Calibri 12 bold", fg="white", height=1, width=w_cps, bd=1, relief=FLAT).grid(row=rind+1, column=2, sticky=N+E, pady=2)

master.bind('<Return>', enterkey)
master.mainloop()
