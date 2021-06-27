import os
import distutils.util
import ast
import log

class ConfigFile:
    switcher = {
        "int": int,
        "bool": bool,
        "str": str,
        "float": float,
        "list": list,
        "dict": dict
    }
    switcherDefaultValues = {
        "int": 0,
        "bool": False,
        "str": "DEFAULTSTRING",
        "float": 0.0,
        "list": [],
        "dict": {}
    }
    def __init__(self, name, allowedEntries, configDirectory="resources", configName="config.txt"): #Defaults to bot
        allowedConfigLines = len(allowedEntries)
        self.name = name
        self.configIntegrityStatus = False
        self.allowedConfigLines = allowedConfigLines
        self.allowedEntries = allowedEntries
        self.configDirectory = configDirectory
        self.configPath = configDirectory+"\\"+configName
        # if len(databases) > 0:
        #     self.databases = databases
        #     self.databasePaths = list(map(lambda database: configDirectory+database, databases))
        log.log(1, f"Received configuration directory as {self.configPath}")
        self.cfgIntegrity(setup=True)

    def configsetup(self):
        log.log(1, f"Started config setup at {self.configDirectory}")
        if not os.path.exists(self.configDirectory): #if the path doesn't exist
            log.log(2, f"Directory missing. Creating directory and file at {self.configDirectory}")
            try:
                os.mkdir(self.configDirectory)
                file = open(self.configPath, "w+")
                self.returnToDefault()
                file.close()
            except:
                log.log(3, "Error while creating configuration...")
        elif not os.path.exists(self.configPath): #if path exists but file doesn't exist
            log.log(2, "Found path, file is missing. Creating configuration.")
            file = open(self.configPath, "w+")
            self.returnToDefault()
            file.close()
        else:
            log.log(1, "Found path and configuration file in directory.")
        # for databasePath in self.databasePaths:
        #     if not os.path.exists(databasePath):
        #         file = open(self.databasePath, "w+")


    def getConfigEntry(self, lineIndex, list=False):
        if not self.configIntegrityStatus:
            self.cfgIntegrity()
        file = open(self.configPath, "r")
        fileLines = file.readlines()
        if fileLines[lineIndex][-1:] == "\n":
            fileLines[lineIndex] = fileLines[lineIndex][:-1]
        if list == True: 
            try:
                returnList = ast.literal_eval(fileLines[lineIndex])
            except:
                return False
            else:
                return returnList
        return ast.literal_eval(fileLines[lineIndex])

    def editConfigEntry(self, lineIndex, *, value="", listType=False, listIndex=0):
        file = open(self.configPath, "r")
        l_lines = file.readlines()
        file.close()
        if listType == "add":
            listvalue = ast.literal_eval(l_lines[lineIndex])
            if type(listvalue) == dict:
                listvalue[listIndex] = value
            else:
                listvalue.append(value)
            l_lines[lineIndex] = str(listvalue)
        elif listType == "remove" or listType == "delete":
            listvalue = ast.literal_eval(l_lines[lineIndex])
            listvalue.pop(listIndex)
            l_lines[lineIndex] = str(listvalue)
        else:
            l_lines[lineIndex] = value+"\n"
        file = open(self.configPath, "w")
        for line in l_lines:
            file.write(line)
        file.close()
        self.configIntegrityStatus = False
        return


    def returnToDefault(self):
        file = open(self.configPath, 'w')
        i = 0
        for i in range(0, len(self.allowedEntries)):
            foundType = False
            if type(self.allowedEntries[i]) == list:
                for acceptedvalue in self.allowedEntries[i]:
                    if acceptedvalue in self.switcher.keys():
                        file.write(str(self.switcherDefaultValues[acceptedvalue])+"\n")
                        foundType = True
                        break
                if not foundType:
                    file.write(str(self.allowedEntries[i][0])+"\n")
            else:
                if self.allowedEntries[i] in self.switcher.keys():
                    file.write(str(self.switcherDefaultValues[self.allowedEntries[i]])+"\n")
                else:
                    file.write(str(self.allowedEntries[i])+"\n")
            i += 1

    def getConfigList(self):
        if not self.configIntegrityStatus:
            self.cfgIntegrity()
        file = open(self.configPath, 'r')
        l_file = file.readlines()
        for i in range(0, len(l_file)):
            if l_file[i][-1:] == "\n":
                l_file[i] = l_file[i][:-1]
            l_file[i] = l_file[i].strip()
        return l_file

    def cfgIntegrity(self, setup=False):
        path = self.configPath
        acceptedValues = self.allowedEntries
        if setup == True:
            self.configsetup()
            setup = False
        file = open(self.configPath, "r")
        l_file = file.readlines()
        for i in range(0, len(l_file)):
            if l_file[i][-1:] == "\n":
                l_file[i] = l_file[i][:-1]
            l_file[i] = l_file[i].strip()
        if len(l_file) != self.allowedConfigLines:
            log.log(2, "Configuration file's line count doesn't match expected. Reverting to default....")
            self.returnToDefault()
            return False
        for i in range(0, len(l_file)): #go through file lines
            t_checked = False
            if type(acceptedValues[i]) == list:
                for acceptedValue in acceptedValues[i]: #go through list inside accepted values
                    try: #get exception if it is a string
                        fileValueWithType = ast.literal_eval(l_file[i])
                        if acceptedValue in self.switcher.keys() and type(fileValueWithType) == self.switcher[acceptedValue]: #if the current line accpeted value is found to be a type,
                                t_checked = True        #then check if the line type is equal to the actual type of the string literal found in the switcher
                                break
                        elif type(fileValueWithType) == type(acceptedValue): # if they are the same type, then we can compare them
                            if acceptedValue == fileValueWithType:
                                t_checked = True
                                break
                    except:
                        if type(acceptedValue) != str:
                            pass
                        else:
                            if acceptedValue == "str":
                                t_checked = True
                                break
                            if acceptedValue == l_file[i]:
                                t_checked = True
                                break
            else: # if accepted values is not a list
                try:  # get exception if it is a string
                    fileValueWithType = ast.literal_eval(l_file[i])
                    if acceptedValues[i] in self.switcher.keys() and type(fileValueWithType) == self.switcher[acceptedValues[i]]:  # if the current line accpeted value is found to be a type,
                        t_checked = True                                                                                            # then check if the line type is equal to the actual type of the string literal found in the switcher
                    if type(fileValueWithType) == type(acceptedValues[i]): #if same type then we can compare
                        if acceptedValues[i] == fileValueWithType:
                            t_checked = True
                except:
                    if type(acceptedValues[i]) != str:
                        pass
                    else:
                        if acceptedValues[i] == "str":
                            t_checked = True
                        elif acceptedValues[i] == l_file[i]:
                            t_checked = True
            if not t_checked and type(acceptedValues[i]) == list:
                self.configIntegrityStatus = False
                log.log(2, f"Configuration corrupt at line {i+1}, resetting to default value from original value: {l_file[i]}")
                foundType = False
                for acceptedvalue in acceptedValues[i]:
                    if acceptedvalue in self.switcher.keys():
                        log.log(2, "Found type in allowed entries, resetting to the default value of the first type that was found")
                        self.editConfigEntry(i, value=str(self.switcherDefaultValues[acceptedvalue]) + "\n")
                        foundType = True
                        break
                if foundType == False:
                    self.editConfigEntry(i, value=str(self.allowedEntries[i][0])+"\n")
                self.cfgIntegrity()
                return
            elif not t_checked:
                self.configIntegrityStatus = False
                log.log(2, f"False config integrity at line {i + 1}, resetting to default from original: {l_file[i]}")
                foundType = False
                if acceptedValues[i] in self.switcher.keys():
                    log.log(2, "Found type in allowed entries, resetting to the default value of the first type that was found")
                    self.editConfigEntry(i, value=str(self.switcherDefaultValues[acceptedValues[i]]) + "\n")
                    foundType = True
                    break
                if foundType == False:
                    self.editConfigEntry(i, value=str(acceptedValues[i])+"\n")
                self.editConfigEntry(i, value=str(acceptedValues[i])+"\n")
                self.cfgIntegrity()
                return
        file.close()
        self.configIntegrityStatus = True
        log.log(1, "Configuration integrity verified")
        return True