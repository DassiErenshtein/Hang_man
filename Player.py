class player:
    def __init__(self,name,id,password):
        self.name=name
        self.id=id
        self.password=password
        self.sum_games=0
        self.last_words=[]
        self.sum_wins=0
    def __str__(self):
        # return "{name:"+self.name+",id:"+str(self.id)+",password:"+self.password+",sum_games:"+str(self.sum_games)+",last_words:"+str(self.last_words)+",sum_wins:"+str(self.sum_wins)+"}"
        return "{"+f"'name':'{self.name}','id':'{str(self.id)}','password':'{self.password}','sum_games':{str(self.sum_games)},'last_words':{str(self.last_words)},'sum_wins':{str(self.sum_wins)}"+"}"