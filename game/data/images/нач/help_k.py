a = """94
61
38
62
43
45
44
64
66
67
65
72
69
73
78
73
87
86
79
80
91
88
89
90
85
124
123
92
90
89
41
42
85
125
42
92
89
120
121
122
126
121""".split()

a = set(map(int, a))
a = list(a)
a.sort()
print(*a)