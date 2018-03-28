#!/usr/bin/env python
from couchbase.bucket import Bucket,SD
import cbargs
my_key ="xattr_demo_doc"
my_doc = { 
        "name"    : "DavidH",
        "task"    : "Testing XATTRS",
        "my_array"  : ["a","b","c"]
         }
my_metadata = {
				"channels": ["users", "customers", "admins"],
				"attachments" : "avatar.png",
				"read_count" : 0,
				"author" : "Haikney",
				"rev": 0
			  }

def runWorkload(bucket,args):
	# Start with a clean slate  make sure the key doesn't exist
	try:
		res = bucket.delete(my_key)
	except Exception as e:
		print str(e)

	res = bucket.set(my_key, my_doc)
	# Subdoc operations to manipulate extended attributes

	res = bucket.mutate_in(my_key,
							# Write a full system extended attribute named _sync
							SD.upsert("_sync",my_metadata,xattr=True),
							# Stamp the CAS and the Value's CRC32c using virtual xattrs 
							SD.upsert("_sync.rev","${Mutation.CAS}",xattr=True,_expand_macros=True))
							# SD.upsert("_sync.body_hash", "${Mutation.value_crc32c}",xattr=True,_expand_macros=True))


	# Read back the xattrs we just wrote
	res = bucket.lookup_in(my_key,SD.get('_sync',xattr=True))
	print res

	# Read the virtual $document attribute
	res = bucket.lookup_in(my_key,SD.get('$document.value_crc32c',xattr=True))
	print res

	# Different style of sub-doc ops to manipulate xattrs
	# res = bucket.mutate_in(my_key, SD.array_append("_sync.channels","AUS",xattr=True))

	# Check we can retrieve deleted bodies
	# res = bucket.delete(my_key)
	# res = bucket.lookup_in(my_key,SD.get('_sync',xattr=True,_access_deleted=True))
	# print res

	# Ready the body (value)
	# res = bucket.get(my_key)
	# print res

if __name__ == "__main__":
  args = cbargs.parseArguments()
  bucket = cbargs.connectToBucket(args)
  runWorkload(bucket,args)

