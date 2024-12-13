from minio import Minio
import sys

client = Minio("localhost:9000", "EXbdQZCGy1cBd0ukS9x0", "wVcW5lUNjbG2mBV8icuXY4MlfopI6zRTrbQgqeq2", secure=False)

bucket = sys.argv[1]
path = sys.argv[2]
object = sys.argv[3]
data = path + object

result = client.fput_object(bucket, object, data)

print(
    "created {0} object; etag: {1}, version-id: {2}".format(
        result.object_name, result.etag, result.version_id
    )
)
