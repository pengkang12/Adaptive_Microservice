import os

def moveLocustResults(testDirPath):
    workingDir = os.getcwd()
    locust_stats = "locust_stats.csv"
    if os.path.isfile(os.path.join(workingDir , locust_stats)):
        if not os.path.exists(testDirPath):
            os.makedirs(testDirPath)
        os.rename(os.path.join(workingDir, locust_stats), os.path.join(testDirPath, locust_stats))
    else:
        print("Unable to find locust_distribution.csv for destination folder %s\n", testDirPath)
