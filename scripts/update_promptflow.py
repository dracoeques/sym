import os, json

from sym.modules.db.db import *
from sym.modules.db.models import *
from sqlalchemy.orm.attributes import flag_modified

prompt_flow_id = 39


def main():

  eng,fact = local_session()
  session = fact()

  payload = new_payload_39()

  flow = session.query(PromptFlow)\
    .filter(PromptFlow.id == prompt_flow_id)\
    .first()
  

  flow.payload = payload
  flag_modified(flow, "payload")
  session.commit()


def new_payload_39():

  payload_str = """{
  "network": {
    "edges": [
      {
        "id": "reactflow__edge-node_1692299040311next-node_1692299201045",
        "source": "node_1692299040311",
        "target": "node_1692299201045",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299201045-node_1692299260875",
        "source": "node_1692299201045",
        "target": "node_1692299260875",
        "sourceHandle": null,
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299260875next-node_1692299272909",
        "source": "node_1692299260875",
        "target": "node_1692299272909",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299272909-node_1692299305813",
        "source": "node_1692299272909",
        "target": "node_1692299305813",
        "sourceHandle": null,
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299305813next-node_1692299318730",
        "source": "node_1692299305813",
        "target": "node_1692299318730",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299318730-node_1692299338313",
        "source": "node_1692299318730",
        "target": "node_1692299338313",
        "sourceHandle": null,
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299338313next-node_1692299355174",
        "source": "node_1692299338313",
        "target": "node_1692299355174",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299355174-node_1692299370242",
        "source": "node_1692299355174",
        "target": "node_1692299370242",
        "sourceHandle": null,
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299260875next-node_1692299507719",
        "source": "node_1692299260875",
        "target": "node_1692299507719",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299305813next-node_1692299507719",
        "source": "node_1692299305813",
        "target": "node_1692299507719",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299338313next-node_1692299507719",
        "source": "node_1692299338313",
        "target": "node_1692299507719",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299370242next-node_1692299507719",
        "source": "node_1692299370242",
        "target": "node_1692299507719",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299507719next-node_1692299833992",
        "source": "node_1692299507719",
        "target": "node_1692299833992",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299689580next-node_1692299866680",
        "source": "node_1692299689580",
        "target": "node_1692299866680",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299866680next-node_1692299885178",
        "source": "node_1692299866680",
        "target": "node_1692299885178",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299833992next-node_1692299885178",
        "source": "node_1692299833992",
        "target": "node_1692299885178",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299260875next-node_1692299689580",
        "source": "node_1692299260875",
        "target": "node_1692299689580",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299305813next-node_1692299689580",
        "source": "node_1692299305813",
        "target": "node_1692299689580",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299338313next-node_1692299689580",
        "source": "node_1692299338313",
        "target": "node_1692299689580",
        "sourceHandle": "next",
        "targetHandle": null
      },
      {
        "id": "reactflow__edge-node_1692299370242next-node_1692299689580",
        "source": "node_1692299370242",
        "target": "node_1692299689580",
        "sourceHandle": "next",
        "targetHandle": null
      }
    ],
    "nodes": [
      {
        "id": "node_1692299040311",
        "data": {
          "label": "start"
        },
        "type": "start",
        "width": 53,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 390.3449960506822,
          "y": 86.34409488514194
        },
        "selected": false,
        "positionAbsolute": {
          "x": 390.3449960506822,
          "y": 86.34409488514194
        }
      },
      {
        "id": "node_1692299201045",
        "data": {
          "label": "text_input"
        },
        "type": "text_input",
        "width": 150,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 191.0231728821409,
          "y": 159.96036923013895
        },
        "selected": false,
        "positionAbsolute": {
          "x": 191.0231728821409,
          "y": 159.96036923013895
        }
      },
      {
        "id": "node_1692299260875",
        "data": {
          "label": "storage"
        },
        "type": "storage",
        "width": 70,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 383.4511038295732,
          "y": 213.03654615118285
        },
        "selected": false,
        "positionAbsolute": {
          "x": 383.4511038295732,
          "y": 213.03654615118285
        }
      },
      {
        "id": "node_1692299272909",
        "data": {
          "label": "text_input"
        },
        "type": "text_input",
        "width": 150,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 190.24594837887912,
          "y": 270.60673536245747
        },
        "selected": false,
        "positionAbsolute": {
          "x": 190.24594837887912,
          "y": 270.60673536245747
        }
      },
      {
        "id": "node_1692299305813",
        "data": {
          "label": "storage"
        },
        "type": "storage",
        "width": 70,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 390.1921222649196,
          "y": 323.1398472618385
        },
        "selected": false,
        "positionAbsolute": {
          "x": 390.1921222649196,
          "y": 323.1398472618385
        }
      },
      {
        "id": "node_1692299318730",
        "data": {
          "label": "text_input"
        },
        "type": "text_input",
        "width": 150,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 191.64098396226825,
          "y": 403.45163043509876
        },
        "selected": false,
        "positionAbsolute": {
          "x": 191.64098396226825,
          "y": 403.45163043509876
        }
      },
      {
        "id": "node_1692299338313",
        "data": {
          "label": "storage"
        },
        "type": "storage",
        "width": 70,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 383.4511038295733,
          "y": 481.55378049247577
        },
        "selected": false,
        "positionAbsolute": {
          "x": 383.4511038295733,
          "y": 481.55378049247577
        }
      },
      {
        "id": "node_1692299355174",
        "data": {
          "label": "text_input"
        },
        "type": "text_input",
        "width": 150,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 191.98726253156406,
          "y": 568.6439551303146
        },
        "selected": false,
        "positionAbsolute": {
          "x": 191.98726253156406,
          "y": 568.6439551303146
        }
      },
      {
        "id": "node_1692299370242",
        "data": {
          "label": "storage"
        },
        "type": "storage",
        "width": 70,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 392.59854183316963,
          "y": 647.5669162589671
        },
        "selected": false,
        "positionAbsolute": {
          "x": 392.59854183316963,
          "y": 647.5669162589671
        }
      },
      {
        "id": "node_1692299507719",
        "data": {
          "label": "prompt"
        },
        "type": "prompt",
        "width": 67,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 254.28558155220554,
          "y": 748.1128105569315
        },
        "selected": true,
        "positionAbsolute": {
          "x": 254.28558155220554,
          "y": 748.1128105569315
        }
      },
      {
        "id": "node_1692299689580",
        "data": {
          "label": "prompt"
        },
        "type": "prompt",
        "width": 67,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 538.8135704979865,
          "y": 749.3878546510291
        },
        "selected": false,
        "positionAbsolute": {
          "x": 538.8135704979865,
          "y": 749.3878546510291
        }
      },
      {
        "id": "node_1692299833992",
        "data": {
          "label": "storage"
        },
        "type": "storage",
        "width": 70,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 264.6846424720193,
          "y": 841.035180970706
        },
        "selected": false,
        "positionAbsolute": {
          "x": 264.6846424720193,
          "y": 841.035180970706
        }
      },
      {
        "id": "node_1692299866680",
        "data": {
          "label": "storage"
        },
        "type": "storage",
        "width": 70,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 535.0421254687706,
          "y": 835.8292206298755
        },
        "selected": false,
        "positionAbsolute": {
          "x": 535.0421254687706,
          "y": 835.8292206298755
        }
      },
      {
        "id": "node_1692299885178",
        "data": {
          "label": "finish"
        },
        "type": "finish",
        "width": 59,
        "height": 39,
        "dragging": false,
        "position": {
          "x": 398.7878290530814,
          "y": 971.255571869302
        },
        "selected": false,
        "positionAbsolute": {
          "x": 398.7878290530814,
          "y": 971.255571869302
        }
      }
    ],
    "viewport": {
      "x": 72.3919951061996,
      "y": -103.27935959387696,
      "zoom": 0.7412319155408158
    }
  },
  "node_data": {
    "node_1692299201045": {
      "id": "node_1692299201045",
      "hint": "",
      "question": "What is your niche?"
    },
    "node_1692299260875": {
      "id": "node_1692299260875",
      "variable_name": "niche"
    },
    "node_1692299272909": {
      "id": "node_1692299272909",
      "hint": "",
      "question": "Describe your unique coaching package offer..."
    },
    "node_1692299305813": {
      "id": "node_1692299305813",
      "variable_name": "offer"
    },
    "node_1692299318730": {
      "id": "node_1692299318730",
      "hint": "",
      "question": "How long have you been doing this?"
    },
    "node_1692299338313": {
      "id": "node_1692299338313",
      "variable_name": "time"
    },
    "node_1692299355174": {
      "id": "node_1692299355174",
      "hint": "",
      "question": "What's your regular free giveaway?"
    },
    "node_1692299370242": {
      "id": "node_1692299370242",
      "variable_name": "giveaway"
    },
    "node_1692299507719": {
      "id": "node_1692299507719",
      "model": "gpt-4",
      "prompt": "Objective: You have interviewed a coach to help them customize these Client Getting Scripts. \nUsing the answers to these questions, customize the following scripts to be most appropriate for a client for this coach. \n\nQuestion 1: What is your niche?\nAnswer 1: My niche is {niche}\nQuestion 2: Describe your unique coaching offer...\nAnswer 2: My coaching package is {offer}\nQuestion 3: How long have you been doing this?\nAnswer 3: I've been at this for {time}\n\nQuestion 4: What's your regular free giveaway?\nAnswer 4: I give away {giveaway}\nInstructions: Customize each of these scripts for the nice, offer, time, and free gift that were indicated by the coach. Use the exact kind of language that a client of this kind of coaching would like to hear and use words and sentences that would flow in a normal conversation by using conjugations like you'll and I'm wherever possible and imagining this was being said in the middle of a normal and regular non-sales conversation. \nHere are each of the scripts:\n1. Qualifying Clients:\n- On a scale of 1-10, how motivated are you to achieve [insert specific goal]?\n- Are you willing to invest in yourself to achieving [insert specific goal]?\n- Are you open to receiving coaching to overcome [insert specific challenge]?\n- Are you willing to invest financially to achieve [insert specific goal]?\n\n2. Transitioning to Offering Coaching Packages:\n- Based on what you told me, the next step is for you to sign up for my [insert specific coaching package].\n\n3. Building Trust and Qualifying:\n- What are the other problems that being [insert specific problem] is causing in your life?\n- What are the other results that achieving [insert specific goal] will give you?\n\n4. Content Creation and Invitations:\n- And if you want my [insert specific recipe or resource], just send me an email.\n- If you're really serious about [insert specific goal], just reach out to me.\n\n5. Offering Support and Help:\n- Let's do a call and I'll help you make a plan to achieve [insert specific goal].\n- I'm here to help you overcome [insert specific problem].\n\n6. Emphasizing Value and Results:\n- Over the next 90 days, you'll achieve [insert specific result].\n- If you want to get great results, faster results, if you want to accelerate your success in [insert specific area or goal], reach out to me.\n\n7. Reassuring Prospective Clients:\n- This is not a pitch for my coaching. I'm here to help you overcome [insert specific problem].\n\n8. Expressing Gratitude:\n- I appreciate your time and consideration in this process. I believe in your potential and I'm excited about the possibility of helping you reach [insert specific goal].\n\n9. Incorporating Storytelling:\n- Let me share a story about a client I worked with who faced similar challenges to [insert specific challenge]...\n\n10. Identifying Money Making Opportunities:\n- Based on our conversation, I believe there are untapped opportunities that can help you accelerate your success in [insert specific area].\n\nCustom Scripts for This Coach: ",
      "system": "You are an expert coach who knows how to communicate effectively to prospects to motivate them to take action in their lives"
    },
    "node_1692299689580": {
      "id": "node_1692299689580",
      "model": "gpt-4",
      "prompt": "Objective: You have interviewed a coach to help them customize these Client Getting Scripts. \nUsing the answers to these questions, customize the following scripts to be most appropriate for a client for this coach. \n\nQuestion 1: What is your niche?\nAnswer 1: My niche is {niche}\nQuestion 2: Describe your unique coaching offer...\nAnswer 2: My coaching package is {offer}\nQuestion 3: How long have you been doing this?\nAnswer 3: I've been at this for {time}\n\nQuestion 4: What's your regular free giveaway?\nAnswer 4: I give away {giveaway}\nInstructions: Customize each of these scripts for the nice, offer, time, and free gift that were indicated by the coach. Use the exact kind of language that a client of this kind of coaching would like to hear and use words and sentences that would flow in a normal conversation by using conjugations like you'll and I'm wherever possible and imagining this was being said in the middle of a normal and regular non-sales conversation. \nHere are each of the scripts:\n11. Highlight Your Value and Results:\n- Over the past [insert specific time period], I've helped clients achieve [insert specific results].\n\n12. Asking for Referrals:\n- Who else do you know that would like to achieve [insert specific goal]?\n- Can you think of anyone in your network who might also benefit from my coaching services in [insert specific area]?\n\n13. Emphasize Your Expertise and Experience:\n- As a coach with [insert number of years] of experience and expertise in [insert specific niche], I have refined my methods and strategies to deliver even greater results.\n\n14. Communicate the Benefits of Investing in Higher-Level Coaching:\n- By investing in higher-level coaching, you will receive more personalized attention, advanced strategies, and a deeper level of support. This will enable you to achieve your goals in [insert specific area or goal] faster and more effectively.\n\n15. Offer a Limited-Time Promotion:\n- For a limited time, I am offering a special promotion where you can lock in my [insert specific coaching service] at a discounted rate. However, please note that my prices will be increasing in the near future, so now is the best time to take advantage of this opportunity.\n\n16. Provide Testimonials and Social Proof:\n- Many of my clients have experienced significant transformations and achieved remarkable results in [insert specific area or goal] through our coaching sessions.\n\n17. Ensuring Comfortable Conversations: \n- I greatly value our coaching relationship and your trust in me. If you know anyone who could benefit from a similar experience in [insert specific area or goal], would you feel comfortable recommending my services?\n\n18. Offering Special Incentives: \n- As a thank you for your referral, I'm offering a special discount on your next coaching session in [insert specific area or goal].\n\n19. Encouraging Ongoing Referrals: \n- Your referral is the highest compliment you can give me. If you know any other individuals who could benefit from my services in [insert specific area or goal] down the line, please don't hesitate to connect them with me.\n\n20. Expressing Gratitude for Referrals: \n- I want to express my deepest gratitude for your willingness to refer my coaching services to others. Your support is invaluable in helping me reach and impact more lives in [insert specific area or goal].\n\nCustom Scripts for This Coach: ",
      "system": "You are an expert coach who knows how to communicate effectively to prospects to motivate them to take action in their lives"
    },
    "node_1692299833992": {
      "id": "node_1692299833992",
      "variable_name": "results1"
    },
    "node_1692299866680": {
      "id": "node_1692299866680",
      "variable_name": "results2"
    },
    "node_1692299885178": {
      "id": "node_1692299885178",
      "makepdf": true,
      "outro_message": "{results1}\n{results2}"
    }
  }
}"""

  payload = json.loads(payload_str, strict=False)
  return payload

if __name__ == "__main__":
  main()