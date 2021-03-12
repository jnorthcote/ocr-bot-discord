Point = namedtuple('Point', ['x', 'y'], verbose=True)
# Field = namedtuple('Field', ['label', 'desc'], verbose=True)

class SectionType(bytes, Enum):
    """
    Coordinate with binary codes that can be indexed by the int code.
    """
    def __new__(cls, value, label, parent, split, dims):
        obj = bytes.__new__(cls, [value])
        obj._value_ = value
        obj.label = label
        obj.parent = parent
        obj.split = split
        obj.dims = dims
        return obj
    IMAGE   = (0, 'Image',   None,  False, Rectangle(0,  0,1440,900))
    HEADER  = (1, 'Header',  IMAGE, False, Rectangle(44, 0,1440,80))
    MATCHUP = (2, 'Matchup', IMAGE, False, Rectangle(124,0,1440,80))


    BL_SCROLL  = (3, 'Scroll',  IMAGE, False, Rectangle(210,0,1440,640))
    BL_ROUND   = (4, 'Round',   SCROLL, False, Rectangle(-1,0,1440,80))
    BL_ENTRY   = (5, 'Entry',   SCROLL, True,  Rectangle(-1,0,720,140))

class Section():
    def __init__(self, dimensions, text):
        self.type = findType(dimensions)
        self.text = text

    def findType(self, dimensions):
        if len(text_annotations) = 0:
            pass

class Rectangle():
    def __init__(self, topLeft, botRight):
        self.topLeft = topLeft
        self.botRight = botRight

    def contains(r1, r2):
       return r1.x1 < r2.x1 < r2.x2 < r1.x2 and r1.y1 < r2.y1 < r2.y2 < r1.y2
    def contains(self, r):


    @classmethod
    def fromVertices(cls, v):
        return cls(v[0].y, v[0].x, (v[1].x - v[0].x), (v[2].y - v[0].y) )
