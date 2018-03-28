#!/usr/bin/env python
 # -*- coding: utf-8 -*-
import urllib, urllib2, cookielib, pprint, json, time, sys, codecs, datetime, re, os
from datetime import datetime,timedelta
import argparse

#sys.stdout = codecs.getwriter('utf8')(sys.stdout)

GERRIT_BASE_URL='http://review.couchbase.org/changes/?q='
HEADERS={ 'Accept': "application/json"}
project_codes = {"ep-engine": "  EP", "memcached" : "  MC", "ns_server": "  NS",
                 "phosphor":" PHO", "couchstore" : "  CS",
                 "platform": "  PF", "tlm": " TLM", "build": "   B", "manifest": " MAN", "moxi": " MOX"}
# def dump(out_string):
#   output_file.write(out_string + '\n')
#   output_file.flush()
projects = ['ep-engine', 'memcached', 'couchstore', 'platform']

good_guys = { "jim": {"username": "jim", "displayname": "Jim"},
             "daver": {"username": "drigby", "displayname": "Dave R"},
             "manu": {"username": "manu", "displayname": "Manu"},
             "dan": {"username": "owend", "displayname": "Daniel"},
             "trond": {"username": "trond", "displayname": "Trond"},
             # "mark": {"username": "mnunberg", "displayname": "Mark N"},
             "sriram": {"username": "sriganes", "displayname": "Sriram"},
             # "will": {"username": "WillGardner", "displayname": "Will"},          
             "james": {"username": "jameseh96", "displayname": "James"},           
             # "ollie": {"username": "OliverMD", "displayname": "Ollie"},
             "paolo": {"username": "paolococchi", "displayname": "Paolo"},
             "prem": {"username": "premkumr", "displayname": "Prem"},
             "tim": {"username": "Tim020", "displayname": "Tim"},
             "pv": {"username": "patrick", "displayname": "Patrick"},
              "simon": {"username": "spjmurray", "displayname": "Simon"}
             }

statusStrings = {
  "MERGED":    '\033[92m' + "✓" + '\033[0m',
  "ABANDONED": 'X',
  "NEW": '+',
  "ACTIVE": 'ACTIVE',
  "DORMANT": 'zzZZ',
  }

base_dir="/Users/dhaikney/dev/gerrit_status/"

alert_file=open("/tmp/alerts.txt",'w')

def get_URL(target_url):
  while True:
    try:
      req = urllib2.Request(target_url,headers=HEADERS)
      return urllib2.urlopen(req, timeout=5).read()
    except Exception as e:
      print ("Could not retrieve URL: " + str(target_url) + str(e))
      time.sleep(1)


def getFullSetOfResults(base_query):
  moreChanges=True
  offset=0
  batch_size = 30 # Number of changes in one request
  change_list=[]
  while moreChanges:
    QUERY_STR=base_query + "&n={0}&start={1}".format(batch_size,offset)
    gerrit_response = get_URL(GERRIT_BASE_URL + QUERY_STR)
    gerrit_json = json.loads(gerrit_response[5:]) # trim the inital garbage
    change_list = change_list + gerrit_json
    moreChanges = gerrit_json != [] and ('_more_changes' in gerrit_json[-1])
    offset += batch_size
  return change_list

def addChangesToOwner(change_list):
  for change in change_list:
    user = change['owner']['username']
    proj = change['project']
    if user not in engineers:
      engineers[user] = {"name": change['owner']['name'], 
                         "ep-engine": [], 
                         "memcached": [],
                         "count": 0}
    engineers[user][proj].append(change['change_id'])
    engineers[user]['count'] += 1

def getEngineersSummary(eng,start_date):
  query="owner:{0}+((status:open)OR(after:{1}))&o=DETAILED_ACCOUNTS".format(eng,start_date)
  return getFullSetOfResults(query)

def getDetailedChangeActivity(eng,start_time):
  query="owner:{0}+after:{1}&o=MESSAGES&o=DETAILED_ACCOUNTS".format(eng,start_time)
  return getFullSetOfResults(query)

def getAllChangesForProject(proj,start_time):
  query="project:{0}+((status:open)OR(after:{1}))&o=DETAILED_ACCOUNTS".format(proj,start_time)
  return getFullSetOfResults(query)

def printTotalChanges():
  result = sorted(engineers, key=lambda x : engineers[x]['count'], reverse=True) 
  ep_total = 0
  memcached_total = 0
  print "Engineer".ljust(22), " Tot", "  MC", "  EP"
  print "=" * 38
  for eng in result:
    name = engineers[eng]['name']
    ep_changes = len(engineers[eng]['ep-engine'])
    memcached_changes = len(engineers[eng]['memcached'])
    total = ep_changes + memcached_changes
    ep_total += ep_changes
    memcached_total += memcached_changes
    print name.ljust(22),  str(total).rjust(4), str(memcached_changes).rjust(4), str(ep_changes).rjust(4)
  print "-" * 38
  grand_total = memcached_total + ep_total
  print "Totals".ljust(22),str(grand_total).rjust(4), str(memcached_total).rjust(4), str(ep_total).rjust(4)

def printEngineersSummary(change_list):
  for change in change_list:
    proj = project_codes[change['project']]
    print change['_number'], proj.rjust(4), change['status'], change['branch'].rjust(8), change['subject']


def printSummaryLine(activity, eng):
  out_string  = (good_guys[eng]['displayname'] + ': ').ljust(10) 
  out_string +=  '\033[92m' + '✓' * activity['merged'] + '\033[0m'
  out_string += '+' * activity['new']
  out_string += 'o' * activity['active']
  out_string += '.' * activity['dormant']
  out_string += 'X' * activity['abandoned']
  print out_string

def summariseProjectActivity(change_set,start_time):
  for eng in good_guys:
    user = good_guys[eng]['username']
    eng_changes=[]
    for change in change_set:
      if change['owner']['username'] == user:
        eng_changes.append(change)
    summariseEngActivity(eng_changes,eng,start_time)  

def summariseEngActivity(change_list, eng,start_time):
  seen_changes=[] # Used to catch duplicates
  activity = { "new": 0, "merged":0, "abandoned" : 0, "dormant" : 0, "active" :0}
  for change in change_list:
    if change["_number"] not in seen_changes:
      seen_changes.append(change["_number"])
      creation_date = datetime.strptime(change['created'][:10], '%Y-%m-%d')
      update_date   = datetime.strptime(change['updated'][:10], '%Y-%m-%d')
      if change['status'] == "MERGED":
        activity['merged'] += 1
      elif change['status'] == "ABANDONED":
        activity['abandoned'] += 1
      elif creation_date >= start_time:
        activity['new'] += 1
        change['status'] = "NEW"
      elif update_date >= start_time:
        change['status'] = "ACTIVE"
        activity['active'] += 1
      else :
        change['status'] = "DORMANT"
        activity['dormant'] += 1
  printSummaryLine(activity,eng) 

def createNotification(eng, change, new=False):
  if not args.notifications:
    return
  name = good_guys[eng]['displayname']
  if new:
    t = '-title "{} created a change"'.format(name)
  elif change['status'] == "MERGED":
    t = '-title "{}\'s change was merged"'.format(name)
  else :
    t = '-title "{}: {}"'.format(name,change['status'])
    # s = '-subtitle "news of  {!r} "'.format(change['owner']['name'])
  m = '-message {!r}'.format(str(change['subject']))
  a = '-appIcon {!r}'.format(str(change['owner']['avatars'][2]['url']))
  change_link = "http://review.couchbase.org/"+str(change['_number'] )
  o = '-open {}'.format(change_link)
  g = '-group ' + eng
  command = '/usr/local/bin/terminal-notifier {}\n'.format(' '.join([m, t, a, o]))
  alert_file.write(command)


def compareChanges(eng, old_change,new_change):
  if old_change['status'] != new_change['status']:
    createNotification(eng,new_change, new=False)

def compareChangeSets(eng, old,new):
  for new_change in new:
    found_change=False
    for old_change in old:

      if old_change['_number'] == new_change['_number']:
        found_change = True
        compareChanges(eng, old_change,new_change)
    if not found_change:
      createNotification(eng,new_change, new=True)

def printChangeSummary(change):
  if change['status'] != "DORMANT":
    print "http://review.couchbase.org/"+str(change['_number'] ) , '{:5}'.format(statusStrings[change['status']]), change['branch'].ljust(8), change['subject']


def printChangeDetails(change):
  print json.dumps(change)
  revs_list=[]
  owner = change['owner']['username']

  for message in change['messages']:
    rev = message['_revision_number']
    text = message['message']
    if 'author' in message:
      author = message['author']['username']
    else:
      author == "gerrit"  
    
    if text.startswith("Uploaded patch set") or text.endswith("was rebased"):
      if  text.endswith("was rebased"):
        rev += 1
      rev = {"id": rev, "reviews": [], "date": message['date'][:16] }
      revs_list.append(rev)
    elif ": Code-Review" in text:
      m = re.match("Patch Set [0-9]*: Code-Review([+-][0-2]).*", text)
      review = {"author": author, "vote": m.groups()[0]}
      revs_list[-1]['reviews'].append(review)
  for rev in revs_list:
    out_string = "V" + str(rev['id']) + ": " + rev['date']
    for review in rev['reviews']:
      out_string += "  " + review['author'] + ": " + review['vote']
    print out_string
    # if author != "buildbot":
    #   print  message['date'][:16], author.ljust(10) , ": " , text.replace('\n', ' ')
    # proj = project_codes[change['project']]
    # print change['_number'], proj.rjust(4), change['status'], change['branch'].rjust(8), change['subject']

def determineNotifications(eng,current_change_set):
  fname = base_dir + eng + '.txt'
  try:
    with open(fname, 'r') as change_set_file:
      old_change_set = json.load(change_set_file)
  except (ValueError, IOError): 
      old_change_set = []
  compareChangeSets(eng, old_change_set,change_set)
  with open(fname, 'w') as change_set_file:
    json.dump(change_set, change_set_file)

def parseArguments():
  parser = argparse.ArgumentParser(description='List changes from gerrit')
  parser.add_argument('--engineers', '-e', choices=good_guys,default=[], nargs='+',help='choose your favourite engineer(s)')
  parser.add_argument('--verbose', '-v', help='Activity on specified engineers changes', action="store_true")
  parser.add_argument('--days', '-d', type=int, default=7, help='number of days history to consider')
  parser.add_argument('--notifications','-n', help='enable OSX notifications', action = "store_true")
  return parser.parse_args()


args = parseArguments()

current_time = datetime.now()
start_time   = current_time - timedelta(days=args.days)
start_time_str    = datetime.strftime(start_time, '%Y-%m-%d')

if args.engineers != []:
  for eng in args.engineers:
    user = good_guys[eng]['username']
    if args.verbose:
      change_set = getDetailedChangeActivity(user,start_time_str)
      for change in change_set:
        printChangeSummary(change)
        printChangeDetails(change)
    else:
      change_set = getEngineersSummary(user,start_time_str)
      summariseEngActivity (change_set,eng,start_time)
      for change in change_set:
        printChangeSummary(change)
      if args.notifications:
        determineNotifications(eng, change_set)
else:
  if args.notifications:
    for eng in good_guys:
      user = good_guys[eng]['username']
      change_set = getEngineersSummary(user,start_time_str)  
      summariseEngActivity (change_set,eng,start_time)
      determineNotifications(eng, change_set)
    # time.sleep(5)   
    # os.system('/usr/local/bin/terminal-notifier -remove ALL')
  elif args.verbose:
    print "cant summarise all project changes yet"
  else: # Summary only 
  	for eng in good_guys:
	  user = good_guys[eng]['username']
	  change_set = getEngineersSummary(user,start_time_str)  
	  summariseEngActivity (change_set,eng,start_time)
	  determineNotifications(eng, change_set)


  # printEngineersSummary(eng_changes)
# else:
#   ep_engine_changes = getAllChangesForProject("ep-engine")
#   memcached_changes = getAllChangesForProject("memcached")
#   addChangesToOwner(ep_engine_changes)
#   addChangesToOwner(memcached_changes)
#   printTotalChanges()
  
