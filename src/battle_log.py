# text_annotations {
#   description: "DEFEAT"
#   bounding_poly {
#     vertices {
#       x: 619
#       y: 62
#     }
#     vertices {
#       x: 824
#       y: 62
#     }
#     vertices {
#       x: 824
#       y: 104
#     }
#     vertices {
#       x: 619
#       y: 104
#     }
#   }
# }
class BattleLog():
    def __init__(self, text_annotations):
        self.sections = analyze(text_annotations)

    def analyze(self, text_annotations):
        if len(text_annotations) = 0:
            pass

        sections = []
        sectionP = None
        for text_annotation in text_annotations:
            section = Section(Rectangle.fromVertices(text_annotation['bounding_poly']['vertices']), text_annotation['description'])
            if sectionP == None:
                sectionP = section

            print text_annotation['restaurant']['name']
