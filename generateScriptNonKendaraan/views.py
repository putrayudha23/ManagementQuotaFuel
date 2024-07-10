from django.shortcuts import render
from django.core.paginator import Paginator
from django.http import HttpResponse
from datetime import datetime
import re
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import subprocess
import os
import gzip
import time
import zipfile

from uploadExcelNonkendaraan.models import NonVehicleMaster
from siteMaster.models import SiteMaster

def index(request):
    if request.user.is_authenticated:
        no_penyalur = ""
        start_date = ""
        end_date = ""
        jenis_skript = ""
        versi_skript = ""

        if request.method == 'POST':
            # Get the values from the form
            no_penyalur = request.POST.get('noPenyalur')
            start_date = request.POST.get('startDate')
            end_date = request.POST.get('endDate')
            jenis_skript = request.POST.get('jenisSkript')
            versi_skript = request.POST.get('versiSkript')

            # Query the database to retrieve data based on the given criteria
            data = NonVehicleMaster.objects.filter(
                site_registration=no_penyalur,
                tgl_awal_rekom=start_date,
                tgl_akhir_rekom=end_date,
                approved_status = True
            )
        else:
           data = []
        
        sites = SiteMaster.objects.filter(deleted=False)
        paginator = Paginator(data, 100)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj, 'sites':sites, 'no_penyalur': no_penyalur, 'start_date': start_date, 'end_date': end_date, 'jenis_skript': jenis_skript, 'versi_skript': versi_skript}

        # You can pass the 'data' to your template for rendering
        return render(request, 'scriptGeneratorNonKendaraan.html', context)
    else:
        return render(request, 'noAccess.html')

@csrf_exempt
def generate_script(request):
    if request.method == 'POST':
        # Retrieve user inputs
        no_penyalur = request.POST.get('noPenyalur')
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        jenis_skript = request.POST.get('jenisSkript')
        versi_skript = request.POST.get('versiSkript')

        if jenis_skript == 'Perpanjangan':
            formatted_end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%d-%b-%Y")

            sql_statement = f"UPDATE TRNQUOTAGROUP SET DATEVALIDFROM='{start_date} 00:00:00.0', DATEVALIDTO='{end_date} 23:59:59.0', LASTUPDATE=UNIX_TIMESTAMP()*1000;\n\nINSERT INTO LOG (CLASS,TYPE,SUBTYPE,LEVEL,CONTENT,TIMESTAMP,PROCESSED) VALUES ('TRNPanel','APP','ON',3,'Customer Update:'+(SELECT COUNT(id)+','+SUM(QUOTAALLOCATED)+','+SUM(QUOTAAVAILABLE)+','+NOW() FROM TRNQUOTACUSTOMER),NOW(),0);"
            # Save the SQL content to a gzipped file
            gzipped_filename = f'Extend_{formatted_end_date}.sql.gz'
            gzipped_path = os.path.join(os.path.dirname(__file__), gzipped_filename)
            with gzip.open(gzipped_path, 'wb') as gz_file:
                gz_file.write(sql_statement.encode())

            adhoc_statement = f'''#!/bin/bash
#
#-----------------------------------------------------------------------
#
# To remove last ship list and add new ship list
# 
#-----------------------------------------------------------------------

echo "Lets check we have valid ship list files. "

DBFILEPATH=Extend_{formatted_end_date}

#Ok lets check the create database file exists.
if [ ! -f /mnt/backup/$DBFILEPATH.sql.gz.cpt ] ; 
	then echo "database create file does not exist...failed!" ; exit 1 ; 
fi

echo "Copying script to a temporary file."
cp /mnt/backup/$DBFILEPATH.sql.gz.cpt /var/tmp/dbscript.sql.gz.cpt 
ccrypt -d -K funky /var/tmp/dbscript.sql.gz.cpt
gunzip -f /var/tmp/dbscript.sql.gz

# Let's run the script 
echo "Executing the DB script."
SQL=/var/tmp/dbscript.sql

read line < /etc/hostname
hostname=$line

echo "Run query in $hostname. "
cat $SQL | java -jar /usr/local/mrc/libs/sqltool.jar --autoCommit $hostname -

# Let's clean the temporary files up
echo "Removing all temporary files."
rm /var/tmp/dbscript.sql


echo "Done."

# Finishing beep
beep -f 700.7 -r 2 -d 200 -l 500
'''
            # Save the SQL content to a gzipped file
            adhoc_filename = f'adhoc_Extend_{formatted_end_date}.sh'
            adhoc_path = os.path.join(os.path.dirname(__file__), adhoc_filename)
            with open(adhoc_path, 'w', newline='') as file:
                file.write(adhoc_statement)

            response_data = {
                'content': sql_statement,
                'filename': gzipped_filename,
                'Adhoc': adhoc_filename
            }

            return JsonResponse(response_data)      
        elif jenis_skript == 'Update ID Nelayan':
            if versi_skript == 'Skript V2':

                # Get data from models where site_registration matches no_penyalur and dates match
                data = NonVehicleMaster.objects.filter(
                    site_registration=no_penyalur,
                    tgl_awal_rekom=start_date,
                    tgl_akhir_rekom=end_date,
                    approved_status = True
                )

                # Initialize an empty SQL script
                sql_statement = "--Delete current data\n"
                sql_statement += "DELETE FROM TRNQUOTACUSTOMER;\n\n"

                # Loop through the data and dynamically insert rows into the SQL script
                for row in data:
                    just_number = int(re.search(r'\d+', row.no_konsumen).group())  # Extract the last three characters from no_konsumen
                    insert_statement = f"--Insert new list kapal\nINSERT INTO TRNQUOTACUSTOMER (ID,CARDNO,TRNQUOTAGROUP_IDGROUP,TRNQUOTAGROUP_IDQUOTA,QUOTAALLOCATED,QUOTAAVAILABLE,QUOTAPRESET,TRANSACTIONCOUNT,QUOTARESETDELETE,QUOTARESETMANUAL,DBREF,DELETED,LASTUPDATE) VALUES ({just_number},'{row.no_konsumen}',2,1,{row.alokasi_volume}*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),({row.alokasi_volume}*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51))-ifnull((select sum(volume)/1000 from trntransactionfuel where registration='{row.no_konsumen}' and reprint=0 and (datetimeslip between TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01'),'YYYY-MM-DD') and now()))*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),0),0,0,0,1,0,0,UNIX_TIMESTAMP()*1000);"
                    sql_statement += insert_statement + "\n\n"

                # Add the rest of the SQL script
                sql_statement += "INSERT INTO TRNQUOTACUSTOMER (ID,CARDNO,TRNQUOTAGROUP_IDGROUP,TRNQUOTAGROUP_IDQUOTA,QUOTAALLOCATED,QUOTAAVAILABLE,QUOTAPRESET,TRANSACTIONCOUNT,QUOTARESETDELETE,QUOTARESETMANUAL,DBREF,DELETED,LASTUPDATE,QUOTAAVAILABLEVOLUMEBEFORE,QUOTAAVAILABLEVOLUMEAFTER,PROCESSED) VALUES (9999,'TERA',2,1,200*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),200*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),0,0,0,1,0,0,UNIX_TIMESTAMP()*1000,0,0,0);\n\n"
                sql_statement += "--Reset quota date\nUPDATE TRNQUOTACUSTOMER SET TRNQUOTAGROUP_IDGROUP=2, TRNQUOTAGROUP_IDQUOTA=1, QUOTARESETDELETE=0, QUOTARESETMANUAL=1, QUOTARESETDATE = TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01'),'YYYY-MM-DD') + INTERVAL '1' MONTH, LASTUPDATE=UNIX_TIMESTAMP()*1000;\n\n"
                formatted_end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                sql_statement += f"--Valid\nUPDATE TRNQUOTAGROUP SET DATEVALIDFROM=TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01 00:00:00.0'),'YYYY-MM-DD HH24:MI:SS.FF'), DATEVALIDTO='{formatted_end_date} 23:59:59.0', LASTUPDATE=UNIX_TIMESTAMP()*1000;\n\n"
                sql_statement += "--Log\nINSERT INTO LOG (CLASS,TYPE,SUBTYPE,LEVEL,CONTENT,TIMESTAMP,PROCESSED) VALUES ('TRNPanel','APP','ON',3,'Customer Update:'+(SELECT COUNT(id)+','+SUM(QUOTAALLOCATED)+','+SUM(QUOTAAVAILABLE)+','+NOW() FROM TRNQUOTACUSTOMER),NOW(),0);\n\n"

                # Save the SQL content to a gzipped file
                gzipped_filename = f'Update_{no_penyalur.replace(" ", "_")}_{end_date}.sql.gz'
                gzipped_path = os.path.join(os.path.dirname(__file__), gzipped_filename)
                with gzip.open(gzipped_path, 'wb') as gz_file:
                    gz_file.write(sql_statement.encode())
                
                adhoc_statement = f'''#!/bin/bash
#
#-----------------------------------------------------------------------
#
# To remove last ship list and add new ship list
# 
#-----------------------------------------------------------------------

echo "Lets check we have valid ship list files. "

DBFILEPATH=Update_{no_penyalur.replace(" ", "_")}_{end_date}

#Ok lets check the create database file exists.
if [ ! -f /mnt/backup/$DBFILEPATH.sql.gz.cpt ] ; 
	then echo "database create file does not exist...failed!" ; exit 1 ; 
fi

echo "Copying script to a temporary file."
cp /mnt/backup/$DBFILEPATH.sql.gz.cpt /var/tmp/dbscript.sql.gz.cpt 
ccrypt -d -K funky /var/tmp/dbscript.sql.gz.cpt
gunzip -f /var/tmp/dbscript.sql.gz

# Let's run the script 
echo "Executing the DB script."
SQL=/var/tmp/dbscript.sql

read line < /etc/hostname
hostname=$line

echo "Run query in $hostname. "
cat $SQL | java -jar /usr/local/mrc/libs/sqltool.jar --autoCommit $hostname -

# Let's clean the temporary files up
echo "Removing all temporary files."
rm /var/tmp/dbscript.sql


echo "Done."

# Finishing beep
beep -f 700.7 -r 2 -d 200 -l 500
'''
                # Save the SQL content to a gzipped file
                adhoc_filename = f'adhoc_Update_{no_penyalur.replace(" ", "_")}_{end_date}.sh'
                adhoc_path = os.path.join(os.path.dirname(__file__), adhoc_filename)
                with open(adhoc_path, 'w', newline='') as file:
                    file.write(adhoc_statement)

                response_data = {
                    'content': sql_statement,
                    'filename': gzipped_filename,
                    'Adhoc': adhoc_filename
                }

                return JsonResponse(response_data)
            elif versi_skript == 'Skript V3':

                # Get data from models where site_registration matches no_penyalur and dates match
                data = NonVehicleMaster.objects.filter(
                    site_registration=no_penyalur,
                    tgl_awal_rekom=start_date,
                    tgl_akhir_rekom=end_date,
                    approved_status = True
                )

                # Initialize an empty SQL script
                sql_statement = "--Delete current data\n"
                sql_statement += "DELETE FROM TRNQUOTACUSTOMER;\n\n"

                # Loop through the data and dynamically insert rows into the SQL script
                for row in data:
                    just_number = int(re.search(r'\d+', row.no_konsumen).group())  # Extract the last three characters from no_konsumen
                    insert_statement = f"--Insert new list kapal\nINSERT INTO TRNQUOTACUSTOMER (ID,CARDNO,TRNQUOTAGROUP_IDGROUP,TRNQUOTAGROUP_IDQUOTA,QUOTAALLOCATED,QUOTAAVAILABLE,QUOTAPRESET,TRANSACTIONCOUNT,QUOTARESETDELETE,QUOTARESETMANUAL,DBREF,DELETED,LASTUPDATE,QUOTAAVAILABLEVOLUMEBEFORE,QUOTAAVAILABLEVOLUMEAFTER,PROCESSED) VALUES ({just_number},'{row.no_konsumen}',2,1,{row.alokasi_volume}*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),({row.alokasi_volume}*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51))-ifnull((select sum(volume)/1000 from trntransactionfuel where registration='{row.no_konsumen}' and reprint=0 and (datetimeslip between TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01'),'YYYY-MM-DD') and now()))*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),0),0,0,0,1,0,0,UNIX_TIMESTAMP()*1000,0,0,0);"
                    sql_statement += insert_statement + "\n\n"

                # Add the rest of the SQL script
                sql_statement += "INSERT INTO TRNQUOTACUSTOMER (ID,CARDNO,TRNQUOTAGROUP_IDGROUP,TRNQUOTAGROUP_IDQUOTA,QUOTAALLOCATED,QUOTAAVAILABLE,QUOTAPRESET,TRANSACTIONCOUNT,QUOTARESETDELETE,QUOTARESETMANUAL,DBREF,DELETED,LASTUPDATE,QUOTAAVAILABLEVOLUMEBEFORE,QUOTAAVAILABLEVOLUMEAFTER,PROCESSED) VALUES (9999,'TERA',2,1,200*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),200*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),0,0,0,1,0,0,UNIX_TIMESTAMP()*1000,0,0,0);\n\n"
                sql_statement += "--Reset quota date\nUPDATE TRNQUOTACUSTOMER SET TRNQUOTAGROUP_IDGROUP=2, TRNQUOTAGROUP_IDQUOTA=1, QUOTARESETDELETE=0, QUOTARESETMANUAL=1, QUOTARESETDATE = TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01'),'YYYY-MM-DD') + INTERVAL '1' MONTH, LASTUPDATE=UNIX_TIMESTAMP()*1000;\n\n"
                formatted_end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                sql_statement += f"--Valid\nUPDATE TRNQUOTAGROUP SET DATEVALIDFROM=TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01 00:00:00.0'),'YYYY-MM-DD HH24:MI:SS.FF'), DATEVALIDTO='{formatted_end_date} 23:59:59.0', LASTUPDATE=UNIX_TIMESTAMP()*1000;\n\n"
                sql_statement += "--Log\nINSERT INTO LOG (CLASS,TYPE,SUBTYPE,LEVEL,CONTENT,TIMESTAMP,PROCESSED) VALUES ('TRNPanel','APP','ON',3,'Customer Update:'+(SELECT COUNT(id)+','+SUM(QUOTAALLOCATED)+','+SUM(QUOTAAVAILABLE)+','+NOW() FROM TRNQUOTACUSTOMER),NOW(),0);\n\n"

                # Save the SQL content to a gzipped file
                gzipped_filename = f'Update_{no_penyalur.replace(" ", "_")}_{end_date}.sql.gz'
                gzipped_path = os.path.join(os.path.dirname(__file__), gzipped_filename)
                with gzip.open(gzipped_path, 'wb') as gz_file:
                    gz_file.write(sql_statement.encode())
                
                adhoc_statement = f'''#!/bin/bash
#
#-----------------------------------------------------------------------
#
# To remove last ship list and add new ship list
# 
#-----------------------------------------------------------------------

echo "Lets check we have valid ship list files. "

DBFILEPATH=Update_{no_penyalur.replace(" ", "_")}_{end_date}

#Ok lets check the create database file exists.
if [ ! -f /mnt/backup/$DBFILEPATH.sql.gz.cpt ] ; 
	then echo "database create file does not exist...failed!" ; exit 1 ; 
fi

echo "Copying script to a temporary file."
cp /mnt/backup/$DBFILEPATH.sql.gz.cpt /var/tmp/dbscript.sql.gz.cpt 
ccrypt -d -K funky /var/tmp/dbscript.sql.gz.cpt
gunzip -f /var/tmp/dbscript.sql.gz

# Let's run the script 
echo "Executing the DB script."
SQL=/var/tmp/dbscript.sql

read line < /etc/hostname
hostname=$line

echo "Run query in $hostname. "
cat $SQL | java -jar /usr/local/mrc/libs/sqltool.jar --autoCommit $hostname -

# Let's clean the temporary files up
echo "Removing all temporary files."
rm /var/tmp/dbscript.sql


echo "Done."

# Finishing beep
beep -f 700.7 -r 2 -d 200 -l 500
'''
                # Save the SQL content to a gzipped file
                adhoc_filename = f'adhoc_Update_{no_penyalur.replace(" ", "_")}_{end_date}.sh'
                adhoc_path = os.path.join(os.path.dirname(__file__), adhoc_filename)
                with open(adhoc_path, 'w', newline='') as file:
                    file.write(adhoc_statement)

                response_data = {
                    'content': sql_statement,
                    'filename': gzipped_filename,
                    'Adhoc': adhoc_filename
                }

                return JsonResponse(response_data)
        elif jenis_skript == 'Penambahan ID Nelayan':
            if versi_skript == 'Skript V2':

                # Get data from models where site_registration matches no_penyalur and dates match
                data = NonVehicleMaster.objects.filter(
                    site_registration=no_penyalur,
                    tgl_awal_rekom=start_date,
                    tgl_akhir_rekom=end_date,
                    approved_status = True
                )

                list_noKonsumen = ', '.join(f"'{row.no_konsumen}'" for row in data)

                # Initialize an empty SQL script
                sql_statement = "--Delete current data\n"
                sql_statement += f"Delete from TRNQUOTACUSTOMER where CARDNO in({list_noKonsumen});\n\n"

                for row in data:
                    just_number = int(re.search(r'\d+', row.no_konsumen).group())  # Extract the last three characters from no_konsumen
                    insert_statement = f"--Insert new list kapal\nINSERT INTO TRNQUOTACUSTOMER (ID,CARDNO,TRNQUOTAGROUP_IDGROUP,TRNQUOTAGROUP_IDQUOTA,QUOTAALLOCATED,QUOTAAVAILABLE,QUOTAPRESET,TRANSACTIONCOUNT,QUOTARESETDELETE,QUOTARESETMANUAL,DBREF,DELETED,LASTUPDATE) VALUES ({just_number},'{row.no_konsumen}',2,1,625*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),(625*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51))-ifnull((select sum(volume)/1000 from trntransactionfuel where registration='{row.no_konsumen}' and reprint=0 and (datetimeslip between TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01'),'YYYY-MM-DD') and now()))*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),0),0,0,0,1,0,0,UNIX_TIMESTAMP()*1000);"
                    sql_statement += insert_statement + "\n\n"

                sql_statement += "--Reset quota date\nUPDATE TRNQUOTACUSTOMER SET TRNQUOTAGROUP_IDGROUP=2, TRNQUOTAGROUP_IDQUOTA=1, QUOTARESETDELETE=0, QUOTARESETMANUAL=1, QUOTARESETDATE = TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01'),'YYYY-MM-DD') + INTERVAL '1' MONTH, LASTUPDATE=UNIX_TIMESTAMP()*1000;\n\n"
                formatted_end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                sql_statement += f"--Valid\nUPDATE TRNQUOTAGROUP SET DATEVALIDFROM=TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01 00:00:00.0'),'YYYY-MM-DD HH24:MI:SS.FF'), DATEVALIDTO='{formatted_end_date} 23:59:59.0', LASTUPDATE=UNIX_TIMESTAMP()*1000;\n\n"
                sql_statement += "--Log\nINSERT INTO LOG (CLASS,TYPE,SUBTYPE,LEVEL,CONTENT,TIMESTAMP,PROCESSED) VALUES ('TRNPanel','APP','ON',3,'Customer Update:'+(SELECT COUNT(id)+','+SUM(QUOTAALLOCATED)+','+SUM(QUOTAAVAILABLE)+','+NOW() FROM TRNQUOTACUSTOMER),NOW(),0);\n\n"
                
                # Save the SQL content to a gzipped file
                gzipped_filename = f'Add_{no_penyalur.replace(" ", "_")}_{end_date}.sql.gz'
                gzipped_path = os.path.join(os.path.dirname(__file__), gzipped_filename)
                with gzip.open(gzipped_path, 'wb') as gz_file:
                    gz_file.write(sql_statement.encode())
                
                adhoc_statement = f'''#!/bin/bash
#
#-----------------------------------------------------------------------
#
# To remove last ship list and add new ship list
# 
#-----------------------------------------------------------------------

echo "Lets check we have valid ship list files. "

DBFILEPATH=Add_{no_penyalur.replace(" ", "_")}_{end_date}

#Ok lets check the create database file exists.
if [ ! -f /mnt/backup/$DBFILEPATH.sql.gz.cpt ] ; 
	then echo "database create file does not exist...failed!" ; exit 1 ; 
fi

echo "Copying script to a temporary file."
cp /mnt/backup/$DBFILEPATH.sql.gz.cpt /var/tmp/dbscript.sql.gz.cpt 
ccrypt -d -K funky /var/tmp/dbscript.sql.gz.cpt
gunzip -f /var/tmp/dbscript.sql.gz

# Let's run the script 
echo "Executing the DB script."
SQL=/var/tmp/dbscript.sql

read line < /etc/hostname
hostname=$line

echo "Run query in $hostname. "
cat $SQL | java -jar /usr/local/mrc/libs/sqltool.jar --autoCommit $hostname -

# Let's clean the temporary files up
echo "Removing all temporary files."
rm /var/tmp/dbscript.sql


echo "Done."

# Finishing beep
beep -f 700.7 -r 2 -d 200 -l 500
'''
                # Save the SQL content to a gzipped file
                adhoc_filename = f'adhoc_Add_{no_penyalur.replace(" ", "_")}_{end_date}.sh'
                adhoc_path = os.path.join(os.path.dirname(__file__), adhoc_filename)
                with open(adhoc_path, 'w', newline='') as file:
                    file.write(adhoc_statement)

                response_data = {
                    'content': sql_statement,
                    'filename': gzipped_filename,
                    'Adhoc': adhoc_filename
                }

                return JsonResponse(response_data)
            elif versi_skript == 'Skript V3':

                # Get data from models where site_registration matches no_penyalur and dates match
                data = NonVehicleMaster.objects.filter(
                    site_registration=no_penyalur,
                    tgl_awal_rekom=start_date,
                    tgl_akhir_rekom=end_date,
                    approved_status = True
                )

                list_noKonsumen = ', '.join(f"'{row.no_konsumen}'" for row in data)

                # Initialize an empty SQL script
                sql_statement = "--Delete current data\n"
                sql_statement += f"Delete from TRNQUOTACUSTOMER where CARDNO in({list_noKonsumen});\n\n"

                for row in data:
                    just_number = int(re.search(r'\d+', row.no_konsumen).group())  # Extract the last three characters from no_konsumen
                    insert_statement = f"--Insert new list kapal\nINSERT INTO TRNQUOTACUSTOMER (ID,CARDNO,TRNQUOTAGROUP_IDGROUP,TRNQUOTAGROUP_IDQUOTA,QUOTAALLOCATED,QUOTAAVAILABLE,QUOTAPRESET,TRANSACTIONCOUNT,QUOTARESETDELETE,QUOTARESETMANUAL,DBREF,DELETED,LASTUPDATE,QUOTAAVAILABLEVOLUMEBEFORE,QUOTAAVAILABLEVOLUMEAFTER,PROCESSED) VALUES ({just_number},'{row.no_konsumen}',2,1,625*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),(625*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51))-ifnull((select sum(volume)/1000 from trntransactionfuel where registration='{row.no_konsumen}' and reprint=0 and (datetimeslip between TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01'),'YYYY-MM-DD') and now()))*(SELECT PRICE FROM TRNPRODUCT WHERE ID=51),0),0,0,0,1,0,0,UNIX_TIMESTAMP()*1000,0,0,0);"
                    sql_statement += insert_statement + "\n\n"

                sql_statement += "--Reset quota date\nUPDATE TRNQUOTACUSTOMER SET TRNQUOTAGROUP_IDGROUP=2, TRNQUOTAGROUP_IDQUOTA=1, QUOTARESETDELETE=0, QUOTARESETMANUAL=1, QUOTARESETDATE = TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01'),'YYYY-MM-DD') + INTERVAL '1' MONTH, LASTUPDATE=UNIX_TIMESTAMP()*1000;\n\n"
                formatted_end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%Y-%m-%d")
                sql_statement += f"--Valid\nUPDATE TRNQUOTAGROUP SET DATEVALIDFROM=TO_DATE(CONCAT(TO_CHAR(CURRENT_DATE,'YYYY-MM'),'-01 00:00:00.0'),'YYYY-MM-DD HH24:MI:SS.FF'), DATEVALIDTO='{formatted_end_date} 23:59:59.0', LASTUPDATE=UNIX_TIMESTAMP()*1000;\n\n"
                sql_statement += "--Log\nINSERT INTO LOG (CLASS,TYPE,SUBTYPE,LEVEL,CONTENT,TIMESTAMP,PROCESSED) VALUES ('TRNPanel','APP','ON',3,'Customer Update:'+(SELECT COUNT(id)+','+SUM(QUOTAALLOCATED)+','+SUM(QUOTAAVAILABLE)+','+NOW() FROM TRNQUOTACUSTOMER),NOW(),0);\n\n"

                # Save the SQL content to a gzipped file
                gzipped_filename = f'Add_{no_penyalur.replace(" ", "_")}_{end_date}.sql.gz'
                gzipped_path = os.path.join(os.path.dirname(__file__), gzipped_filename)
                with gzip.open(gzipped_path, 'wb') as gz_file:
                    gz_file.write(sql_statement.encode())
                
                adhoc_statement = f'''#!/bin/bash
#
#-----------------------------------------------------------------------
#
# To remove last ship list and add new ship list
# 
#-----------------------------------------------------------------------

echo "Lets check we have valid ship list files. "

DBFILEPATH=Add_{no_penyalur.replace(" ", "_")}_{end_date}

#Ok lets check the create database file exists.
if [ ! -f /mnt/backup/$DBFILEPATH.sql.gz.cpt ] ; 
	then echo "database create file does not exist...failed!" ; exit 1 ; 
fi

echo "Copying script to a temporary file."
cp /mnt/backup/$DBFILEPATH.sql.gz.cpt /var/tmp/dbscript.sql.gz.cpt 
ccrypt -d -K funky /var/tmp/dbscript.sql.gz.cpt
gunzip -f /var/tmp/dbscript.sql.gz

# Let's run the script 
echo "Executing the DB script."
SQL=/var/tmp/dbscript.sql

read line < /etc/hostname
hostname=$line

echo "Run query in $hostname. "
cat $SQL | java -jar /usr/local/mrc/libs/sqltool.jar --autoCommit $hostname -

# Let's clean the temporary files up
echo "Removing all temporary files."
rm /var/tmp/dbscript.sql


echo "Done."

# Finishing beep
beep -f 700.7 -r 2 -d 200 -l 500
'''
                # Save the SQL content to a gzipped file
                adhoc_filename = f'adhoc_Add_{no_penyalur.replace(" ", "_")}_{end_date}.sh'
                adhoc_path = os.path.join(os.path.dirname(__file__), adhoc_filename)
                with open(adhoc_path, 'w', newline='') as file:
                    file.write(adhoc_statement)

                response_data = {
                    'content': sql_statement,
                    'filename': gzipped_filename,
                    'Adhoc': adhoc_filename
                }

                return JsonResponse(response_data)

    # Handle other cases or errors
    return HttpResponse('Invalid request.')

@csrf_exempt
def encrypt_script_endpoint(request):
    if request.method == 'POST':
        # Get the gzipped file name and passphrase from the request
        gz_filename = request.POST.get('gzFilename')
        adhoc = request.POST.get('adhoc')
        passphrase = "funky"

        # Define the path for the encrypted .cpt file (output file)
        cpt_filename = gz_filename + ".cpt"
        cpt_adhoc = adhoc + ".cpt"

        # Create the path for the gzipped file
        base_dir = os.path.dirname(os.path.abspath(__file__))

        gzipped_path = os.path.join(base_dir, gz_filename)
        cpt_path = os.path.join(base_dir, cpt_filename)
        adhoc_path = os.path.join(base_dir, adhoc)
        cpt_adhoc_path = os.path.join(base_dir, cpt_adhoc)

        # Run ccencrypt to encrypt the gzipped file
        try:
            # Invoke ccencrypt with subprocess; handle passphrase securely
            ccrypt_path = os.path.join(base_dir, 'ccrypt-1.11.cygwin-x64', 'ccrypt.exe')

            ccencrypt_command = [ccrypt_path, '-e', '-K', passphrase, gzipped_path]
            subprocess.run(ccencrypt_command, shell=True, check=True)

            ccencrypt_command_adhoc = [ccrypt_path, '-e', '-K', passphrase, adhoc_path]
            subprocess.run(ccencrypt_command_adhoc, shell=True, check=True)

            # Create a ZIP archive containing both .cpt and adhoc.cpt files
            with zipfile.ZipFile(cpt_filename, 'w') as zipf:
                zipf.write(cpt_path, os.path.basename(cpt_path))
                zipf.write(cpt_adhoc_path, os.path.basename(cpt_adhoc_path))

            # Return the ZIP archive as a response
            with open(cpt_filename, 'rb') as zip_file:
                response = HttpResponse(zip_file, content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename={cpt_filename}'

            # Delete the gzipped file
            os.remove(cpt_path)
            os.remove(cpt_adhoc_path)
            os.remove(cpt_filename)

            return response

        except subprocess.CalledProcessError:
            # Handle errors or provide an appropriate response
            return JsonResponse({'success': False, 'error': 'Encryption failed'})

    # Handle GET requests or other HTTP methods
    return HttpResponse(status=405)