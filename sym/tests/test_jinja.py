
from jinja2 import Environment, BaseLoader

template_parameters = {
  "response": "Yes please!",
  "challenge": "I can't seem to stop my dog from barking",
  "null": "To address the challenge of excessive barking, here are some helpful tips for dog training:\n\n1. Identify the triggers: Pay attention to what triggers your dog's barking. Is it people passing by, other animals, or certain sounds? Understanding the triggers can help you address the underlying cause.\n\n2. Teach the \"quiet\" command: Train your dog to respond to the \"quiet\" command. Start by saying \"quiet\" in a calm, firm tone when your dog barks. Once your dog stops barking, reward them with a treat and praise. Practice this command consistently in different situations.\n\n3. Provide mental and physical stimulation: Dogs often bark out of boredom or excess energy. Make sure your dog receives enough mental and physical exercise throughout the day. Engage them in activities like puzzle toys, obedience training, and regular walks or play sessions.\n\n4. Desensitize to triggers: Gradually expose your dog to the triggers that cause barking, starting with a low-intensity version of the trigger. For example, if your dog barks at strangers, start by having a friend stand at a distance where your dog notices them but doesn't bark excessively. Reward your dog for staying calm and gradually decrease the distance over time.\n\n5. Use positive reinforcement: Reward your dog for calm behavior and for not barking when they would typically do so. This reinforces the desired behavior and helps your dog understand what is expected of them.\n\n6. Seek professional help if needed: If the barking problem persists despite your efforts, consider consulting with a professional dog trainer or behaviorist. They can provide personalized guidance and training techniques specific to your dog's needs.\n\nRemember, consistency, patience, and positive reinforcement are key when training your dog. With time and effort, you can effectively reduce excessive barking and improve your dog's behavior.",
  "messages": [
    {
      "role": "assistant",
      "content": "What is a current challenge you're facing with your dog training?"
    },
    {
      "role": "user",
      "content": "Given this challenge: I can't seem to stop my dog from barking provide helpful advice on dog training"
    },
    {
      "role": "assistant",
      "content": "To address the challenge of excessive barking, here are some helpful tips for dog training:\n\n1. Identify the triggers: Pay attention to what triggers your dog's barking. Is it people passing by, other animals, or certain sounds? Understanding the triggers can help you address the underlying cause.\n\n2. Teach the \"quiet\" command: Train your dog to respond to the \"quiet\" command. Start by saying \"quiet\" in a calm, firm tone when your dog barks. Once your dog stops barking, reward them with a treat and praise. Practice this command consistently in different situations.\n\n3. Provide mental and physical stimulation: Dogs often bark out of boredom or excess energy. Make sure your dog receives enough mental and physical exercise throughout the day. Engage them in activities like puzzle toys, obedience training, and regular walks or play sessions.\n\n4. Desensitize to triggers: Gradually expose your dog to the triggers that cause barking, starting with a low-intensity version of the trigger. For example, if your dog barks at strangers, start by having a friend stand at a distance where your dog notices them but doesn't bark excessively. Reward your dog for staying calm and gradually decrease the distance over time.\n\n5. Use positive reinforcement: Reward your dog for calm behavior and for not barking when they would typically do so. This reinforces the desired behavior and helps your dog understand what is expected of them.\n\n6. Seek professional help if needed: If the barking problem persists despite your efforts, consider consulting with a professional dog trainer or behaviorist. They can provide personalized guidance and training techniques specific to your dog's needs.\n\nRemember, consistency, patience, and positive reinforcement are key when training your dog. With time and effort, you can effectively reduce excessive barking and improve your dog's behavior."
    },
    {
      "role": "assistant",
      "content": "Would you like to know more about our 12 week dog training program?"
    }
  ],
  "text": "Yes please!"
}


system = """
    Hello world: {{text}}
"""
jinja_env = Environment(loader=BaseLoader)
system_template = jinja_env.from_string(system)
generated_system = system_template.render(template_parameters)

print(generated_system)