
from typing import List, Any

from dataclasses import dataclass

@dataclass
class Context:
    context_vector: List[float] = None #what is the context of the prediction ie: it's their birthday
    task_vector: List[float] = None #what is the task to be accomplished ie: write an email
    sender_vector: List[float] = None #who is sending this info
    reciever_vector: List[float] = None #who is recieving this



@dataclass
class ContextualPrediction:
    """ Given this context, how relevant is the target data for accomplishing this task
    """
    
    context: Context = None
    target: List[float] = None #target item vector

    rating: float = None #value from 0 -> 1 of how relevant this item is in this context

    item_id: int = None  #id of original item
    item_type: str = None #item type, message, rating etc. 



#A list of prompt runs 
#context -> results vectorized
#

class ContextualPredictor:

    def predict(self, Context) -> List[ContextualPrediction]:
        """ Given a context, a task, a sender and a reciever 
        
            predict which components are most relevant to the task at hand


            Task:
                Write an Email to {profile} explaining blockchain
            
            Predicted context: 
                profile is an INTJ 
                profile likes to have things explained to them simply and elegantly like carl sagan

            Write a message to {profile} asking if they would like to go to the new batman movie

            For context: 
                profile is an INTP and they love dark and broody gothic action movies

        """
        pass

