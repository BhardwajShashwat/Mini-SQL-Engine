# Mini-SQL-Engine
A mini​ sql engine which runs simple SQL queries using ​a command line interface

This mini-SQL-Engine was made using python3. To run a query A, we simply run 'python3 20161187.py "(contents of query a)"'
in the command line

Example: 
python3 20161187.py "select * from table A;"

Types of queries which can be run by the Engine:
1. Selecting all records in a table or tables : (select * from table1;)
2. Aggregates- min,max,sum,avg: (select min(A) from table1;)
3. Projecting columns using select
4. Using 'distinct' keyword in queries: (Select distinct col1, col2 from table_name;)
5. Select with where from one or more tables : (Select col1,col2 from table1,table2 where col1 = 10 AND col2 = 20;)
Note: Step 5 only works with a maximum of one AND/OR operator and no NOT operator
6. Projection of one or more(including all the columns) from two tables with one join
condition :(Select * from table1, table2 where table1.col1=table2.col2;)
