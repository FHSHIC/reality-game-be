import json
import os
import uuid



class MockDb:
    def __init__(self, collectName):
        dbs = dict()

        dbList = ["users", "levels", "hints", "dramas", "teams"]
        jsonList = ["UserMock.json", "LevelMock.json", "HintMock.json", "DramaMock.json", "TeamMock.json"]
        
        self.dbMap = {}

        for i, db in enumerate(dbList):
            with open(f"{os.path.dirname(__file__)}/{jsonList[i]}") as f:
                dbs[db] = json.load(f)
            self.dbMap[db] = jsonList[i]
                
        self.colName = collectName
        self.col = dbs[collectName]
        self.colId = [colData["_id"] for colData in self.col]
    
    def find(self, filte: dict = None) -> list:
        return list(filter(lambda x: [x[f] == filte[f] for f in filte.keys()], self.col))
    
    def find_one(self, dataId) -> dict | None:
        result = list(filter(lambda x: x["_id"] == dataId, self.col))
        return result[0] if len(result) > 0 else None
    
    def update_one(self, dataId, updateData) -> int:
        for i, data in enumerate(self.col):
            if data["_id"] != dataId:
                continue
            for updateDataKey in updateData.keys():
                data[updateDataKey] = updateData[updateDataKey]
            del(self.col[i])
            if i == len(self.col):
                self.col.append(data)
                break
            self.col.insert(i, data)
            break
        with open(f"{os.path.dirname(__file__)}/{self.dbMap[self.colName]}", 'w') as f:
            f.write(json.dumps(self.col))
        return 0
    
    def insert_one(self, insertData: dict) -> dict:
        while not insertData.get("_id"):
            dataId = uuid.uuid4().hex
            if dataId not in self.colId:
                insertData["_id"] = dataId
                self.colId.append(dataId)
                break
            
        self.col.append(insertData)
        with open(f"{os.path.dirname(__file__)}/{self.dbMap[self.colName]}", 'w') as f:
            f.write(json.dumps(self.col))
        return insertData
    
    