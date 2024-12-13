from minio import Minio
import sys

client = Minio("localhost:9000", "EXbdQZCGy1cBd0ukS9x0", "wVcW5lUNjbG2mBV8icuXY4MlfopI6zRTrbQgqeq2", secure=False)

bucket = sys.argv[1]

objects = client.list_objects(bucket)
for obj in objects:
    print(obj.object_name, obj.size)
