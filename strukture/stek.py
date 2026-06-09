class Stek:
    def __init__(self):
        self.data=[]
    
    def push(self,el):
        self.data.append(el)
    
    def pop(self):
        if self.isEmpty():
            return None
        return self.data.pop()
    
    def isEmpty(self):
        return len(self.data)<1
    
    def size(self):
        return len(self.data)
