obj=open("abcd.txt","w")
obj.write("Python xin chao cac ban")
obj.close()
obj1=open("abcd.txt","r")
s=obj1.read()
print s
obj1.close()
obj2=open("abcd.txt","r")
s1=obj2.read(21)
print s1
obj2.close()