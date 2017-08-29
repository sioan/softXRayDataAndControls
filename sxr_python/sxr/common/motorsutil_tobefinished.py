from motor import motor


def motor_list(self):
  motors = self.__dict__.keys()
  motors.sort()
  ret = []
  for m in motors:
    try:
      if ( self.__dict__[m].__name__ == "xpp motor class" ):
        ret.append(m)
    except:
      pass
  for i in range(1,11):
    ret.append("filt[%d]" % i)
  ret.sort()
  return ret


def repr(self):
  ret = "defined motors:"
  motors = self.__dict__.keys()
  motors.sort()
  for m in motors:
    try:
      if ( self.__dict__[m].__name__ == "xpp motor class" ):
        ret += "\n%s:\n\t%s" % (m,self.__dict__[m].__repr__())
    except:
      pass
  for i in range(1,11):
    cmd  = "self.__dict__['filt'][%d].__repr__()" % i
    h = eval(cmd)
    ret += "\nfilt[%d]:\n\t%s" % (i,h)
  return ret

def SAVE(self):
  fields = "offset description low_limit high_limit"
  motors = self.__dict__.keys()
  motors.sort()
  names=[]
  for m in motors:
    try:
      if ( self.__dict__[m].__name__ == "xpp motor class" ):
        if  ( (m.find("lcls_") == -1) & (m.find("homs_") == -1) ):
          names.append(m)
    except:
        pass
  import time
  fname  = time.strftime("%Y%m%d_%H%M%S")
  fname += ".save"
  import os;
  myprint("saving data in %s/%s" % (os.getcwd(),fname))
  fout   = open(fname,"w")
  fout.write("name")
  for f in fields.split():
    fout.write("||%s" % f)
  fout.write("\n")
  for n in names:
    m=eval("self.%s" % n)
    r="%s||" % n
    for f in fields.split():
      r += str(m.get_field(f))
      r += "||"
    myprint(r)
    fout.write("%s\n" % r)
  fout.close()

def LOAD(self,fname):
  fields = "offset description low_limit high_limit"
  fin  = open(fname,"r")
  header = fin.readline().rstrip()
  fields = header.split("||")[1:]
  for l in fin:
    line = l.rstrip()
    values = line.split("||")
    mname  = values[0]
    values = values[1:]
    for i in range(len(fields)):
      cmd = "self.%s.change_pv_value('%s','%s')" % (mname,fields[i],values[i])
      eval(cmd)
  fin.close()

def save_config(self,name=""):
  fields = "readback offset description dial_low_limit dial_high_limit"
  names = self.__motor_list()
  import time
  if (name == ""):
    fname  = time.strftime("%Y%m%d_%H%M%S") + "_config"
    fname += ".config_save"
  else:
    fname  = time.strftime("%Y%m%d_%H%M%S") + "_" + name
    fname += ".config_save"
  import os;
  myprint("saving data in %s/%s" % (os.getcwd(),fname))
  fout   = open(fname,"w")
  fout.write("name")
  for f in fields.split():
    fout.write("||%s" % f)
  fout.write("\n")
  for n in names:
    if (n.find("lcls_") == 0):
      continue
    m=eval("self.%s" % n)
    r="%s||" % n
    for f in fields.split():
      r += str(m.get_field(f))
      r += "||"
    myprint(r)
    fout.write("%s\n" % r)
  fout.close()

def has_changed(self,name,what,v_in_file,tolerance=1e-3):
   current = eval("self.%s.get_field('%s')" % (name,what))
   # if float
   try:
     current=float(current)
     v_in_file=float(v_in_file)
     check = ( abs(current-v_in_file) > tolerance )
   # if string
   except:
     check = ( v_in_file != current )
   return (check,current,v_in_file)

def myeval(s):
  """ Useful for debugging without actually moving things """
   print s
  eval(s)


def list_config(self):
  print "this has to be done" 

def load_config(self,fname=""):
  if (fname == ""):
    self.__list_config()
  fields = "readback offset description dial_low_limit dial_high_limit"
  fin  = open(fname,"r")
  header = fin.readline().rstrip()
  fields = header.split("||")[1:]
  tomove=dict()
  tomove["name"]=[]
  tomove["what"]=[]
  tomove["current"]=[]
  tomove["vfile"]=[]
  tomove["cmd"]=[]
  for l in fin:
    line = l.rstrip()
    v = line.split("||")
    mname  = v[0]
    if ( mname.find("homs_") > -1):
      myprint("Skipping HOMS mirrors ...")
      pass
    values = v[1:]
    ## take care for the offset first
    for f in fields:
      idx = fields.index(f); what=fields[idx]; value=values[idx]
      (c,current,vfile)=self.__has_changed(mname,what,value)
      if (c):
        tomove["name"].append(mname); tomove["what"].append(what); tomove["vfile"].append(vfile); tomove["current"].append(current)
        if (what == "readback"):
          cmd = "self.%s.move(%s)" % (mname,vfile)
        else:
          cmd = "self.%s.change_pv_value(%s,%s)" % (mname,what,vfile)
        tomove["cmd"].append(cmd)
  fin.close()
  if (len(tomove["name"]) == 0):
    print "No motors found that have to be moved"
    return
  print "|%5s|%15s|%15s|%15s|->%15s|" % ("idx","name","field","current","infile")
  for i in range(len(tomove["name"])):
    print "|%5d|%15s|%15s|%15s|->%15s|" % (i,tomove["name"][i],
                                       tomove["what"][i],
                                       tomove["current"][i],
                                       tomove["vfile"][i])
  repl=raw_input("enter yes to change them all or space separated list of numbers ?\n")
  if (repl=="yes"):
    list = range(len(tomove["name"]))
  elif ( repl.split(" ")>0):
      list=repl.split()
  else:
      list=()
  if (len(list)!=0):
    for i in list:
      eval(tomove["cmd"][int(i)])
      myprint("%s(%s)->%s" % (tomove["name"][int(i)],tomove["what"][int(i)],tomove["vfile"][int(i)]))
