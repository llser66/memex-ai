from app.database.chroma import collection


print("Collection名称：")
print(collection.name)

print()

print("Chroma数据数量：")
print(collection.count())

print()

print("Chroma数据：")

result = collection.get()

print(result)