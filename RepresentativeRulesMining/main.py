from job import job
from sys import exit

# CAVEAT: CHARACTER '/' IS ASSUMED NOT TO OCCUR AT ALL IN THE DATASET

# EXAMPLES OF USE OF THE job CLASS FOR RUNNING SLATT
# FOR REPRESENTATIVE RULES MINING

# use Borgelt's apriori to compute all frequent closures
# for a dataset and a support bound (in [0,1]):
# items may be strings, not just numbers
todayjob = job("./datasets/test",0.4)
##todayjob = job(".datasets/retail",0.0005)
##todayjob = job(".datasets/retail",0.001)
##todayjob = job(".datasets/adult",0.01)
##todayjob = job(".datasets/adult",0.005)
##todayjob = job(".datasets/accidents",0.5)
##todayjob = job(".datasets/accidents",0.4)


# compute representative rules with Kryszkiewicz incomplete heuristic,
# write the rules into a file 
todayjob.run("GenRR",0.7,show=False,outrules=True)

# compute B* basis, show in console and do not write on file 
todayjob.run("RRGenerator",0.8,show=True,outrules=False)

# compute representative rules, show in console and write on file
todayjob.run("RRClosureGenerator",0.9,show=True,outrules=True)



