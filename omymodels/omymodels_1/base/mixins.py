class EqualByNameMixIn:

    def __eq__(self, __value: object) -> bool:
        if self.__class__ != __value.__class__:
            return False
        if self.name == __value.name:
            return True
