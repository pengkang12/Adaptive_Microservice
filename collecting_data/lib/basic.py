import os

def testDirInit(expName, data_dir):
    # go to previous directory
    workingDir = os.getcwd()
    testDirStr = os.path.join(workingDir, data_dir)
    testDirStr = os.path.join(testDirStr, expName)
    if not os.path.exists(testDirStr):
        os.makedirs(testDirStr)
    return testDirStr

