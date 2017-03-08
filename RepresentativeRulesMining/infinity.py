class inft:
    def __lt__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other,long):
            return False
##        elif isinstance(other, inft):
##            return False
        else: 
            raise Exception("I can't compare infinity with this class") 

    def __le__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other,long):
            return False
##        elif isinstance(other, inft):
##            return True
        else: 
            raise Exception("I can't compare infinity with this class")
    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other,long):
            return inft()
##        elif isinstance(other, inft):
##            return True
        else: 
            raise Exception("I can't compare infinity with this class")
    def __rmul__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other,long):
            return inft()
##        elif isinstance(other, inft):
##            return True
        else: 
            raise Exception("I can't compare infinity with this class")
    def __gt__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other,long):
            return True
##        elif isinstance(other, inft):
##            return False
        else: 
            raise Exception("I can't compare infinity with this class")
    def __ge__(self, other):
        if isinstance(other, int) or isinstance(other, float) or isinstance(other,long):
            return True
##        elif isinstance(other, inft):
##            return True
        else: 
            raise Exception("I can't compare infinity with this class")
    def __repr__(self):
        return u'inf'

infinity = inft()

if __name__ == '__main__':
    infty = inft()
    print infty <= 3, infty >= 3
