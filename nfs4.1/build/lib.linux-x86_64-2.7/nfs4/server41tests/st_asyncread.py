from st_create_session import create_session
from xdrdef.nfs4_const import *
  
from environment import check, checklist, fail, create_file, open_file, close_file
from environment import open_create_file_op

from xdrdef.nfs4_type import *
# from xdrdef.nfs4_type import creatverfattr, fattr4, stateid4, locker4, lock_owner4
# from xdrdef.nfs4_type import open_to_lock_owner4
import nfs_ops
from gtk._gtk import ARG_CHILD_ARG
op = nfs_ops.NFS4ops()
import threading


def expect(res, seqid):
    """Verify that open result has expected stateid.seqid"""
    got = res.resarray[-2].stateid.seqid
    if got != seqid:
        fail("Expected open_stateid.seqid == %i, got %i" % (seqid, got))
        


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
    data = "write test data"
    res = sess1.compound([op.putfh(fh), op.write(stateid, 0, FILE_SYNC4, data),op.read(stateid,0,5)])
    check(res)
    print("came here",res)
   
    
    
    #print("data from read",res1.resarray[-1].data)
    asyre = threading.Event()
    
    def pre_hook(arg, env):
        print "In client data",arg
        print "opcbasync_read Id", arg.opcbasync_read
        print "Req Id",arg.opcbasync_read.argok4.reqid
        env.notify = asyre.set
        
    
    sess1.client.cb_pre_hook(OP_CB_ASYNC_READ, pre_hook)
    """ 
        TODO:have to generate reqId randomly. Append clientid also as it is a distributed
                                            System.
    """
    res1 = sess1.compound([op.putfh(fh), op.async_read(1214,stateid,0,10)])
    check(res1)
    print("got initial response")
    asyre.wait() 