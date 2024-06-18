import tkinter as tk 
from tkinter import filedialog
import ast

class CodeSmellDetectionAndRefactor:
    def __init__(self):
        self.setGuiLayoutConstants()
        self.setGuiLayout()

    def setGuiLayoutConstants(self):
        self.windowWidth = 1000
        self.windowHeight = 800
        self.title = "Code Smell Detection & Refactoring Tool"
        self.uploadFileText= "Please upload a file"
        self.fontStyle= ("Helvetica", 15, "bold")
        self.uploadBtnText = "Upload File"
        self.buttonWidth = 35
        self.buttonHeight = 2
        self.refactorButtonText="Do you want to Refactor Code? Click Here!"
        self.refreshButtonText = "Refresh Screen"
        self.empty = ""
        self.outputWidth = 100
        self.outputHeight = 60
        self.pady = 15

    def setGuiLayout(self):
        self.guiLayout= tk.Tk()
        self.guiLayout.title(self.title)
        self.guiLayout.geometry(f"{self.windowWidth}x{self.windowHeight}") 
        self.guiHeader = tk.Label(self.guiLayout, text=self.uploadFileText, font=self.fontStyle)
        self.uploadBtn = tk.Button(self.guiLayout, text=self.uploadBtnText, command=self.onClickUploadFile, width=self.buttonWidth, height=self.buttonHeight)
        self.refactorBtn = tk.Button(self.guiLayout, text=self.refactorButtonText, command=self.onClickUploadFile, state=tk.DISABLED, width=self.buttonWidth, height=self.buttonHeight)
        self.refreshBtn = tk.Button(self.guiLayout, text=self.refreshButtonText, command=self.initVariables, width=self.buttonWidth, height=self.buttonHeight)
        self.duplicateDetectionLabel = tk.Label(self.guiLayout, text=self.empty, font=self.fontStyle)
        self.outputField = tk.Text(self.guiLayout, width=self.outputWidth, height=self.outputHeight)
        self.scrollBar = tk.Scrollbar(self.guiLayout, command=self.outputField.yview) #vertical scrollbar for output
        self.scrollBar.pack(side=tk.RIGHT, fill=tk.Y) #properties
        self.outputField.config(yscrollcommand=self.scrollBar.set) # outputText widget configured to use the scrollbar
        elements_to_pack = [self.guiHeader, self.uploadBtn, self.refactorBtn, self.duplicateDetectionLabel, self.refreshBtn, self.outputField]
        [element.pack(pady=self.pady) for element in elements_to_pack] #Set properties of every element
        self.guiLayout.mainloop()


    def initVariables(self):
        self.parsedFileTree = ""
        self.outputMessage = ""
        self.duplicateFunctionsDict = {}
        self.dupThreshold = 0.75
        self.valueOne = 1.0
        self.duplicateDetectionLabel.config(text=self.empty)
        self.outputField.delete(self.valueOne, tk.END)  # Clear existing text
        self.refactorBtn.config(state=tk.DISABLED)
        self.fileExtension =("Python files", "*.py")
        self.locText = ""
        self.paramsText = ""
        self.locThreshold = 15
        self.parameterThreshold = 3
        self.true = True
        self.false = False
        
    def onClickUploadFile(self):
        self.initVariables()
        self.uploadFile()
        if self.parsedFileTree != self.empty:
            self.processFile()

    def uploadFile(self):
        actionRead = "r"
        try:
            filePathInput = filedialog.askopenfilename(filetypes=[self.fileExtension])
            if filePathInput:
                with open(filePathInput, actionRead) as filePathInput:
                    fileContents = filePathInput.read()
                self.parsedFileTree = ast.parse(fileContents) 
            else:
                self.duplicateDetectionLabel.config(text="File upload cancelled by the user!")
        except Exception as err:
            print(f"Some error occured: {err}")

    def processFile(self):
        listOfFunctions = self.parseFileForFunctions()
        duplicateCodeExists =  self.detectDuplicateFunctions(listOfFunctions)
       
        if self.outputMessage == self.empty:
            self.duplicateDetectionLabel.config(text="No code smells found in the uploaded code!")
            self.outputField.delete(self.valueOne, tk.END)  # Clear existing text
            self.refactorBtn.config(state=tk.DISABLED)
        else:
            self.outputField.delete(self.valueOne, tk.END)  # Clear existing text
            self.outputField.insert(tk.END, self.outputMessage)  # Insert new text
            if duplicateCodeExists:
                self.duplicateDetectionLabel.config(text="Code smells found in the uploaded code! \nDuplicate code detected!")
                self.refactorBtn.config(state=tk.NORMAL, command=self.onClickRefactorCode)
            else: self.duplicateDetectionLabel.config(text="Code smells found in the uploaded code!")
    
    def createOutputMessages(self):
            self.outputMessage = "Please Note:\nThe threshold for LONG METHOD = 15 ; LONG PARAMETER = 3 ; \nJACCARD'S SIMILARITY INDEX = 0.75\n\n" 
            self.outputMessage += '***----------------------OUTPUT-------------------------***'
           
            if self.locText != self.empty:
                self.outputMessage += "\n\nFunctions whose Lines of Code have exceeded the threshold value:\n"
                self.outputMessage += self.locText + "\n\n"

            if self.paramsText != self.empty:
                self.outputMessage += "\n\nFunctions whose Parameters have exceeded the threshold value:\n"
                self.outputMessage +=  self.paramsText + "\n\n"


    def parseFileForFunctions(self):
        listOfFunctions = []

        for node in self.parsedFileTree.body:
            if isinstance(node, ast.FunctionDef):
                self.detectCodeSmells(node)
                listOfFunctions.append(node)

            elif isinstance(node, ast.ClassDef): 
                for node in node.body:
                    if isinstance(node, ast.FunctionDef):
                        self.detectCodeSmells(node)
                        listOfFunctions.append(node)

        if self.locText != self.empty or self.paramsText != self.empty:
            self.createOutputMessages()
            
        return listOfFunctions 
    

    def detectCodeSmells(self, node):
        numOfLinesOfCode = 0
        countOne = 1

        for eachNode in ast.walk(node):
            if isinstance(eachNode, ast.stmt):
                numOfLinesOfCode += countOne

        numOfLinesOfCode -= countOne                       #-1 to account for the included defination name
        numOfParameters = len(node.args.args) 

        if numOfLinesOfCode > self.locThreshold and numOfParameters > self.parameterThreshold:
            self.locText += f"\n\nFunction {node.name}() \nNumber of Lines of Code found: {numOfLinesOfCode} \n"
            self.paramsText += f"\n\nFunction {node.name}() \nNumber of Parameters found: {numOfParameters} \n"
        
        elif numOfLinesOfCode > self.locThreshold and numOfParameters <= self.parameterThreshold:
            self.locText += f"\n\nFunction {node.name}() \nNumber of Lines of Code found: {numOfLinesOfCode} \n"
        
        elif numOfLinesOfCode <= self.locThreshold and numOfParameters > self.parameterThreshold:
            self.paramsText += f"\n\nFunction {node.name}() \nNumber of Parameters found: {numOfParameters} \n"
        

    def detectDuplicateFunctions(self,listOfFunctions):
        duplicateCodeExists = self.false
        firstTimeDuplicateFound = self.true
        countOne = 1

        for index1 in range(0, len(listOfFunctions)):
            strCode1 = ast.unparse(listOfFunctions[index1])

            for index2 in range(index1 + countOne, len(listOfFunctions)):
                strCode2 = ast.unparse(listOfFunctions[index2])

                if self.jaccardSimilarity(strCode1, strCode2) > self.dupThreshold:
                    if firstTimeDuplicateFound:
                        self.outputMessage += "\n\nDuplicate code exists between these set of Functions:"
                        firstTimeDuplicateFound = self.false
                        duplicateCodeExists = self.true
                
                    self.addFunctionsToDuplicateList(listOfFunctions[index1], listOfFunctions[index2])
                    self.outputMessage += "\n\n\n" + f"{listOfFunctions[index1].name}()" + " & " + f"{listOfFunctions[index2].name}()"
        return duplicateCodeExists      
        
    def jaccardSimilarity(self,function1, function2):
        function1 = set(function1.split()) #SET= {'def', 'self.result', '=', '0'......}
        function2 = set(function2.split())
        intersection = len(function1.intersection(function2)) #Common no. of elements eg: 3
        union = len(function1) + len(function2) - intersection #A + B - C #total unique elements
        if union != 0:
            return intersection / union
        else:
            return 0

    def addFunctionsToDuplicateList(self, node1, node2):
        # Add set of duplicate functions to the dictionary
        if node2 not in self.duplicateFunctionsDict:
            if node1 in self.duplicateFunctionsDict:
                self.duplicateFunctionsDict[node2] = self.duplicateFunctionsDict[node1]
            else:
                self.duplicateFunctionsDict[node2] = [node1]

    def writeFile(self,refactoredCode):
        actionWrite = "w"
        try: 
            filePath = filedialog.asksaveasfilename(filetypes=[self.fileExtension])
            if filePath:
                if filePath:
                    with open(filePath, actionWrite) as file:
                        file.write(refactoredCode)
                self.duplicateDetectionLabel.config(text=f"Refactored code downloaded successfully in the following location: {filePath}")
            else:
                self.duplicateDetectionLabel.config(text=f"Refactored code was not saved!")
        except Exception as err:
            print(f"Some error occured: {err}")


    def refactorDuplicateFunctions(self):
        code =[]
        for node in self.parsedFileTree.body:
            if not(isinstance(node, (ast.ClassDef, ast.FunctionDef))): #ANY other expressions 
                code.append(node)
                
            elif isinstance(node, ast.ClassDef):
                # Append the class definition without its body
                code.append(ast.ClassDef( name=node.name, bases=node.bases, keywords=node.keywords, body=[], decorator_list=node.decorator_list))
                for node in node.body:
                    if node not in self.duplicateFunctionsDict: #if the node is not in the list of duplicates 
                        code.append(node)
            
            elif isinstance(node, ast.FunctionDef) and node not in self.duplicateFunctionsDict: #if the node is not in the list of duplicates 
                code.append(node)
        return ast.unparse(code)
    
    def refactorFunctionCalls(self, code):
        for key, value in self.duplicateFunctionsDict.items():     
            code = code.replace(key.name, value[0].name)
        return code
    
    def onClickRefactorCode(self):
        unParsedCode = self.refactorDuplicateFunctions()
        refactoredCode = self.refactorFunctionCalls(unParsedCode)
        self.writeFile(refactoredCode)

    
cdr = CodeSmellDetectionAndRefactor()
