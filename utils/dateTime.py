from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class TimeDate:
    def __init__(self, tz = "Asia/Taipei"):
        self.tz = ZoneInfo(tz)
    
    def now(self):
        return datetime.now(tz=self.tz)
    
    def compareAThanB(self, aDateTime: datetime, bDateTime: datetime) -> bool:
        """_summary_
        比對 A 與 B 的時間大小，
        如果 A 大，則 True
        否則 False
        若 A == B，則 return None
        
        Args:
            aDateTime (datetime): a 的時間
            bDateTime (datetime): b 的時間

        Returns:
            _type_: bool
        """
        aDateTime = aDateTime.replace(tzinfo=self.tz)
        bDateTime = bDateTime.replace(tzinfo=self.tz)
        return aDateTime > bDateTime if aDateTime != bDateTime else None
    
    def deltaTime(self, timeFrom, deltaSeconds: int) -> datetime:
        if timeFrom == "now":
            timeFrom = self.now()
        return timeFrom + timedelta(seconds=int(deltaSeconds))
    
    def format(self, datetimeTime: datetime) -> str:
        return datetimeTime.isoformat(timespec="seconds")
    
    def toDateTime(self, datetimeString: str) -> datetime:
        return datetime.fromisoformat(datetimeString).replace(tzinfo=self.tz)