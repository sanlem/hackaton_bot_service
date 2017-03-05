class Machine:
    def __init__(self, guide):
        self.guide = guide
        self.stateline = []
        self.current_question = self.guide['questions']['start']
        self.stateline.append('start')

    def next_state(self, answer_id):
        answers = self.current_question['answers']
        result = {}
        if answers:
            next_answs_ids = [answer['next'] for answer in answers]
            if answer_id in next_answs_ids:
                self.stateline.append(str(answer_id))
                self.current_question = self.guide['questions'][str(answer_id)]
                # print('new state: ', self.current_question)
                # print(self.current_question['answers'])
                result['description'] = self.current_question['description']
                result['answers'] = answers
            else:
                raise KeyError
        else:
            result['answers'] = None

        return result
