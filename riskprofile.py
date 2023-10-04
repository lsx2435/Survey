class RiskQuestion:
    def __init__(self, questionText, weight = 1):
        self.questionText = questionText
        self.weight = weight
        self.answers = []    
    
class RiskQuestionAnswer:
    def __init__(self, answerText, score, selected = False):
        self.answerText = answerText
        self.score = score
        self.selected = selected

class RiskQuestionnaire:
    def __init__(self):
        self.questions = []

    def loadQuestionnaire(self, riskQuestionFile, riskAnswerFile):
        import pandas as pd 
        riskQuestion = pd.read_excel(riskQuestionFile).reset_index()
        riskAnswers = pd.read_excel(riskAnswerFile).reset_index()
        
        Questions = riskQuestion.reset_index()
        for index, row in Questions.iterrows():
            self.questions.append((RiskQuestion(row['QuestionText'], row['QuestionWeight'])))
            answers = riskAnswers[(riskAnswers['QuestionID']==row['QuestionID'])]
            for indexA, rowA in answers.iterrows():
                self.questions[index].answers.append(
                RiskQuestionAnswer(rowA['AnswerText'], rowA['AnswerValue']))

    
    def answerQuestionnaire(self):
        import string
        for i in range(len(self.questions)):
            question = self.questions[i]
            print(question.questionText)
            for n in range(len(question.answers)):
                answer = question.answers[n]
                print(str(string.ascii_uppercase[n]) + ": " + answer.answerText)
            nChosen = int(input("다음 중 선택하세요:"))
            self.questions[i].answers[ord(nChosen)-64].selected = True
            print("\n")
    
    def answerScore(self, answerText):
        score = 0#[] 
        for question in self.questions:
            for answer in question.answers:
                for element in answerText:
                    if element in answer.answerText:
                        #score.append(answer.score)
                        score += answer.score
        return(score)
