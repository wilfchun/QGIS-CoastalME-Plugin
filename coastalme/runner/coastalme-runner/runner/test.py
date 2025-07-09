import re

test_string = 'abc_~s1~_~s2~_~s3~_~e1~.csv'

x = re.findall(r"(~s\d~)", test_string)
print(x)