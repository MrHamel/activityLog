#!/bin/env python

'''RHEL Distributed Python Core'''
import argparse, sys, os, shlex, subprocess, tarfile, time

'''Let's get into the real DB management.'''
import sqlalchemy

'''Why not let it phone home when something goes arye.'''
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

'''General Linux Related Functions'''
def get_hostname():
	try:
		with open("/etc/hostname", "r") as hostnamefile:
			return hostnamefile.read
	except IOError:
		print("Unable to open /etc/hostname.")
		return False

	return False

def root_fs_mountable():
	try:
		with open("/proc/mounts", "r") as mountfile:
			for line in mountfile:
				if " / " in line and " rw," in line: return True
	except IOError:
		print("Unable to open /proc/mounts.")
		return False

	return False

def test_file_writable():
	try:
		with open("/activityLog_test", "w") as testfile:
			testfile.write("This is only a test.")
		os.remove("/activityLog_test")
		return True
	except IOError:
		print("Unable to create test file in /.")
		return False

	return False

def get_loadavgs(): return os.loadavg()

def run_shell_cmd(cmd):
	args = shlex.split(cmd)
	# This is a blocking shell command call.
	subprocess.call(args, stdout=open('/root/activityLog/shellcmd-run.log', 'w'))

	with open("/root/activityLog/shellcmd-run.log", "r") as shellfile:
		data = shellfile.readlines()

	os.remove("/root/activityLog/shellcmd-run.log")
	return data

def get_top_data():
	try:
		with open("/root/.toprc", "r") as topfile:
			data = topfile.readlines()
	except IOError:
		data = [""]

	with open("/root/.toprc", "w") as topfile:
		topfile.write('RCfile for \"top with windows\"\n')
		topfile.write("Id:a, Mode_altscr=0, Mode_irixps=1, Delay_time=3.000, Curwin=0\n")
		topfile.write("Def	 fieldscur=AEHIOQTWKNMbcdfgjplrsuvyzX\n")
		topfile.write("		winflags=30137, sortindx=10, maxtasks=0\n")
		topfile.write("		summclr=1, msgsclr=1, headclr=3, taskclr=1\n")
		topfile.write("Job	 fieldscur=ABcefgjlrstuvyzMKNHIWOPQDX\n")
		topfile.write("		winflags=62777, sortindx=0, maxtasks=0\n")
		topfile.write("		summclr=6, msgsclr=6, headclr=7, taskclr=6\n")
		topfile.write("Mem	 fieldscur=ANOPQRSTUVbcdefgjlmyzWHIKX\n")
		topfile.write("		winflags=62777, sortindx=13, maxtasks=0\n")
		topfile.write("		summclr=5, msgsclr=5, headclr=4, taskclr=5\n")
		topfile.write("Usr	 fieldscur=ABDECGfhijlopqrstuvyzMKNWX\n")
		topfile.write("		winflags=62777, sortindx=4, maxtasks=0\n")
		topfile.write("		summclr=3, msgsclr=3, headclr=2, taskclr=3\n")

	topdata = run_shell_cmd("top -bH -n1")

	if data != [""]:
		with open("/root/.toprc", "w") as topfile:
			topfile.write(''.join(data))
	else:
		os.remove("/root/.toprc")

	return topdata

def run_sql_cmd(cmd):
	# Supports mysql, postgresql, mssql, oracle and sqlite.
	# Engine Format: engine://user:password@ip:port/database
	# Read for more info: http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html
	engine = sqlalchemy.create_engine('')

	# PostgreSQL: sql = text('SELECT * FROM pg_stat_activity');
	# MySQL + oracle: sql = text('show full processlist;')
	# MSSQL: sql = text('sp_who2;')
	# SQLite: lol what.
	result = engine.execute('')
	names = []
	for row in result:
		names.append(row[0])

	print names

'''RHEL Related Functions'''

def detect_rhel_ver():
	try:
		with open("/etc/redhat-release", "r") as verfile:
			# Make an array of any numbers (including floating points) in the string specified. - Regex explanation for Joe.
			data = verfile.read.findall(r"[-+]?\d*\.*\d+")

		# Since this is RHEL based, we only need the major version number.
		return data[0]
	except IOError:
		print("Unable to open /etc/redhat-release.")
		return False

	return False

'''Script Releated Functions'''
def timestamp(): return time.strftime("%m_%d_%Y-%H_%M_%S")

def create_targz(name, file):
	try:
		with tarfile.open("/root/activityLog/" + name, "w:gz") as archive:
			archive.add("/root/activityLog/" + file, arcname=file)
		return True
	except IOError:
		print("Unable to save into activityLog archive.")
		return False

	return False

def alert_qn_support():
	msg = MIMEMultipart()
	msg['From'] = "activitylog_s@domain.tld"
	msg['To'] = "support@domain.tld"
	msg['Subject'] = "Activity Log Report - "

	body = "Python Test Email"
	msg.attach(MIMEText(body, 'plain'))

	text = msg.as_string()
	server.sendmail(fromaddr, toaddr, text)

def setup():
	if os.getlogin() != "root":
		print("You need to be root to run this script.")
		exit(-2)

	if root_fs_mountable and test_file_writable:
		if not os.path.exists("/root/activityLog"): os.makedirs("/root/activityLog")

def main():
	parser=argparse.ArgumentParser()
	#parser.add_argument('foo', nargs='+')

	#if len(sys.argv)==1:
	#	parser.print_help()
	#	sys.exit(1)

	args=parser.parse_args()

	setup()

	hostname = get_hostname()

	#rhel_version = detect_rhel_ver()
	topdata = get_top_data()
	loadavgs = get_loadavgs()
	netbandwidth = run_shell_cmd("netstat -i")
	netdaemons = run_shell_cmd("netstat -plunt")
	netconnect = run_shell_cmd("netstat -W")

	# sqldiag = get_sql_data();

	'''Time to write everything to file.'''

	filename = timestamp() + ".log"
	with open("/root/activityLog/" + filename, "w") as activityLog:
		activityLog.write(''.join(topdata))
		activityLog.write("\n\n\n\n\n\n\n")
		activityLog.write("Throughput on Network Interfaces:\n")
		activityLog.write(''.join(netbandwidth))
		activityLog.write("\n\n")
		activityLog.write("Daemons and Open Ports List:\n")
		activityLog.write(''.join(netdaemons))
		activityLog.write("\n\n")
		activityLog.write("Network Connections:\n")
		activityLog.write(''.join(netconnect))
		activityLog.write("\n\n\n\n\n")
		activityLog.write("SQL Queries Active at " + timestamp())

	create_targz("activityLog.tar.gz", filename)
	os.remove("/root/activityLog/" + filename)

	# Email Support
	# alert_support()

if __name__ == "__main__": main()
