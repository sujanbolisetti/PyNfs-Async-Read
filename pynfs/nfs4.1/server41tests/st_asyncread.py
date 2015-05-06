from st_create_session import create_session
from xdrdef.nfs4_const import *
  
from environment import check, checklist, fail, create_file, open_file, close_file
from environment import open_create_file_op
from nfs4lib import use_obj

from xdrdef.nfs4_type import *
import datetime
import nfs_ops

from gtk._gtk import ARG_CHILD_ARG
op = nfs_ops.NFS4ops()

import threading
import time


def expect(res, seqid):
    """Verify that open result has expected stateid.seqid"""
    got = res.resarray[-2].stateid.seqid
    if got != seqid:
        fail("Expected open_stateid.seqid == %i, got %i" % (seqid, got))
        
count = 0
seqId=0

def getReqId():
    global seqId
    seqId = seqId + 1
    return seqId

def testAsyncRead(t, env):
    """Do a simple ASYNCREAD
    
    FLAGS: asyncread all
    CODE: ASYNC1
    """
    sess1 = env.c1.new_client_session(env.testname(t))
    owner = open_owner4(0, "My Open Owner")
    res = create_file(sess1, env.testname(t))
    check(res)
    expect(res, seqid=1)
    fh = res.resarray[-1].object
    stateid = res.resarray[-2].stateid
    stateid.seqid = 0
    #f = open("/home/sujan/Documents/pynfs/nfs4.1/data.txt","r")
    data = "Testing testAsyncRead Test Case"
    res = sess1.compound([op.putfh(fh), op.write(stateid, 0, FILE_SYNC4,data)])
    check(res)
    asyre = threading.Event()
    
    def pre_hook(arg, env):
        print "received callback for testAsyncRead with reqId",arg.opcbasync_read.argok4.reqid
        env.notify = asyre.set
        
        
    sess1.client.cb_pre_hook(OP_CB_ASYNC_READ, pre_hook)
    reqId = getReqId()
    async_res = sess1.compound([op.putfh(fh), op.async_read(reqId,stateid,0,10,0)])
    check(async_res)
    asyre.wait() 


def receivedHk1(arg):
    print "received callback for reqId",arg.opcbasync_read.argok4.reqid
   
def receivedHk2(arg):
    print "received callback for reqId",arg.opcbasync_read.argok4.reqid
       
def testMultipleAsyncReads(t,env):
    """Do a multiple Async READ
    
    FLAGS: asyncread all
    CODE: ASYNC2
    """
    global count
    count = 0
    sess1 = env.c1.new_client_session(env.testname(t))
    owner = open_owner4(0, "My Open Owner")
    res = create_file(sess1, env.testname(t))
    check(res)
    expect(res, seqid=1)
    fh = res.resarray[-1].object
    stateid = res.resarray[-2].stateid
    stateid.seqid = 0
    #f = open("/home/sujan/Documents/pynfs/nfs4.1/data.txt","r")
    data = "Testing testMultipleAsyncReads Test Case"
    res = sess1.compound([op.putfh(fh), op.write(stateid, 0, FILE_SYNC4,data)])
    check(res)
    asyre = threading.Event()
    reqIdHookMap = {}
    
    def pre_hook(arg, env):
        global count
        reqIdHookMap[arg.opcbasync_read.argok4.reqid](arg) 
        count = count +1
        # waiting until two requests are done
        if count==2:
            env.notify = asyre.set
     
    sess1.client.cb_pre_hook(OP_CB_ASYNC_READ, pre_hook) 
    
    reqId = getReqId()
    reqIdHookMap[reqId] = receivedHk1
    res1 = sess1.compound([op.putfh(fh), op.async_read(reqId,stateid,0,10,0)])
    check(res1)
    reqId=getReqId()
    reqIdHookMap[reqId] = receivedHk2
    res2 = sess1.compound([op.putfh(fh), op.async_read(reqId,stateid,7,15,0)])
    check(res2)
    asyre.wait() 
    

def testEOFInAsyncRead(t,env):
    """Do a EOF In Async READ
    
    FLAGS: asyncread
    CODE: ASYNC3
    """
    global count
    count = 0
    sess1 = env.c1.new_client_session(env.testname(t))
    owner = open_owner4(0, "My Open Owner")
    res = create_file(sess1, env.testname(t))
    check(res)
    expect(res, seqid=1)
    fh = res.resarray[-1].object
    stateid = res.resarray[-2].stateid
    stateid.seqid = 0
    data = "write test data"
    res = sess1.compound([op.putfh(fh), op.write(stateid, 0, FILE_SYNC4, data)])
    check(res)
    asyre = threading.Event()
     
    def pre_hook(arg, env):
        if not arg.opcbasync_read.argok4.eof:
            fail("EOF not set on async read")
        else:
            print "Success in EOF"
        env.notify = asyre.set
         
     
    sess1.client.cb_pre_hook(OP_CB_ASYNC_READ, pre_hook)
    reqId=getReqId()
    res1 = sess1.compound([op.putfh(fh), op.async_read(reqId,stateid,0,1000,0)])
    
    check(res1)
    
    asyre.wait() 
    
def testAsyncReadInDifferentSessions(t,env):
    """Do a Async READ In Different Sessions
     
    FLAGS: asyncread all
    CODE: ASYNC4
    """
    global count
    count = 0
    sess1 = env.c1.new_client_session(env.testname(t))
    owner = open_owner4(0, "My Open Owner")
    res = create_file(sess1, env.testname(t))
    check(res)
    expect(res, seqid=1)
    fh = res.resarray[-1].object
    stateid = res.resarray[-2].stateid
    stateid.seqid = 0
    data = "write test data"
    res = sess1.compound([op.putfh(fh), op.write(stateid, 0, FILE_SYNC4, data)])
    check(res)
    
    asyre = threading.Event()
      
    def pre_hook(arg, env):
        global count
        count = count+1
        print "received callback for reqId",arg.opcbasync_read.argok4.reqid
        if count == 2:  
            env.notify = asyre.set
          
    sess2 = env.c1.new_client_session(env.testname(t))
     
    sess1.client.cb_pre_hook(OP_CB_ASYNC_READ, pre_hook)
    sess2.client.cb_pre_hook(OP_CB_ASYNC_READ, pre_hook)
    reqId=getReqId()
    res1 = sess1.compound([op.putfh(fh), op.async_read(reqId,stateid,0,10,0)])
    check(res1)
    sess2.client.cb_pre_hook(OP_CB_ASYNC_READ, pre_hook)
    reqId=getReqId()
    res1 = sess2.compound([op.putfh(fh), op.async_read(reqId,stateid,4,8,0)])
     
    check(res1)
    asyre.wait() 
    
    
    
    
    



    
