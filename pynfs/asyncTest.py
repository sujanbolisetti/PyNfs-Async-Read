from st_create_session import create_session
from xdrdef.nfs4_const import *

from environment import check, checklist, fail, create_file, open_file, close_file
from environment import open_create_file_op
from xdrdef.nfs4_type import open_owner4, openflag4, createhow4, open_claim4
from xdrdef.nfs4_type import creatverfattr, fattr4, stateid4, locker4, lock_owner4
from xdrdef.nfs4_type import open_to_lock_owner4
import nfs_ops
op = nfs_ops.NFS4ops()
import threading

def test_async_read():
    sess1 = env.c1.new_client_session(env.testname(t))
    owner = open_owner4(0, "My Open Owner")
    res = create_file(sess1, env.testname(t))
    check(res)
    expect(res, seqid=1)
    fh = res.resarray[-1].object
    stateid = res.resarray[-2].stateid
    stateid.seqid = 0
    data = "write test data"
    res = sess1.compound([op.putfh(fh), op.write(stateid, 5, FILE_SYNC4, data)])
    check(res)
    res = sess1.compound([op.putfh(fh), op.async_read(1, 0, 5)])
    check(res)
    